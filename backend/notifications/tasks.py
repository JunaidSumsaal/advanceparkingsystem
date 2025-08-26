import requests
import json
import logging
from django.utils import timezone
from django.db import transaction
from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Notification, PushSubscription
from .utils import broadcast_ws_to_user, send_web_push, get_distance_km
from .emailer import send_email_notification

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_notification_async(self, user_id, title, body, type_="general", extra=None):
    """
    Save → Serialize → Send via WebSocket → Try Push → Try Email
    """
    notif = Notification.objects.create(
        user_id=user_id,
        title=title,
        body=body,
        type=type_,
        status="pending",
        delivered=False,
    )

    try:
        broadcast_ws_to_user(user_id, notif)
    except Exception:
        pass

    delivered = False

    # Push Subscriptions
    for sub in PushSubscription.objects.filter(user_id=user_id):
        ok, _ = send_web_push(sub, {"title": title, "body": body})
        if ok:
            delivered = True

    # Email fallback
    user = User.objects.filter(id=user_id).only("email").first()
    if user and user.email:
        try:
            send_email_notification(user.email, title, body)
            delivered = True
        except Exception:
            pass

    notif.delivered = delivered
    notif.status = "sent" if delivered else "pending"
    notif.sent_at = timezone.now()
    notif.save(update_fields=["delivered", "status", "sent_at"])
    return notif.id


@shared_task(rate_limit="30/m")
def booking_reminder_task(booking_id):
    from parking.models import Booking
    from notifications.models import Notification

    try:
        b = Booking.objects.select_related(
            "user", "parking_spot").get(id=booking_id)
    except Booking.DoesNotExist:
        return None

    if not b.user_id or not b.parking_spot:
        return None

    Notification.objects.create(
        user=b.user,
        title="⏰ Booking Reminder",
        body=f"Your booking for {b.parking_spot.name} is active. End it when you leave.",
        type="booking_reminder",
        status="pending",
        delivered=False,
        sent_at=timezone.now(),
    )

    return True


@shared_task
def daily_digest_for_provider(provider_id):
    from parking.models import Booking, Provider

    try:
        provider = Provider.objects.select_related("user").get(id=provider_id)
    except Provider.DoesNotExist:
        return None

    active = Booking.objects.filter(
        parking_spot__provider_id=provider_id, is_active=True
    ).count()

    body = f"Daily digest: {active} active bookings."

    if provider.user_id:
        return send_notification_async.delay(
            provider.user_id,
            "📊 Daily Digest",
            body,
            "general"
        )
    return None


@shared_task(rate_limit="60/m")
def send_pending_notifications(batch_size=50):
    pending = Notification.objects.filter(
        delivered=False, status="pending")[:batch_size]

    for n in pending:
        # Public notifications (broadcast within 10km)
        if n.is_public:
            lat = getattr(n, "extra", {}).get("lat")
            lng = getattr(n, "extra", {}).get("lng")
            spot_name = getattr(n, "extra", {}).get(
                "spot_name", "Parking Spot")

            if not lat or not lng:
                logger.warning(
                    f"Public notification {n.id} missing lat/lng, skipping")
                continue

            users = User.objects.exclude(latitude=None).exclude(longitude=None)
        else:
            # Private notification → just the target user
            users = [n.user] if n.user else []

        for user in users:
            subs = PushSubscription.objects.filter(user=user)
            if not subs.exists():
                continue

            # Distance filter only for public notifications
            send_to_user = True
            distance = None
            if n.is_public and user.latitude and user.longitude:
                distance = get_distance_km(
                    (lat, lng),
                    (user.latitude, user.longitude),
                )
                send_to_user = distance is not None and distance <= 10

            if not send_to_user:
                continue

            delivered = False
            for sub in subs:
                try:
                    body = n.body
                    if n.is_public and distance is not None:
                        body += f"\n📍 {spot_name} is {distance:.1f} km away."

                    resp = requests.post(
                        sub.endpoint,
                        data=json.dumps({
                            "title": n.title,
                            "body": body,
                            "type": n.type,
                        }),
                        headers={"Content-Type": "application/json"},
                        timeout=5,
                    )
                    if resp.status_code in [200, 201]:
                        delivered = True
                except requests.exceptions.RequestException as e:
                    logger.error(f"Push error for sub {sub.id}: {e}")

            # 🔹 Mark delivered / failed
            if delivered:
                with transaction.atomic():
                    n.delivered = True
                    n.status = "sent"
                    n.sent_at = timezone.now()
                    n.save(update_fields=["delivered", "status", "sent_at"])
            else:
                n.save(update_fields=["status"])
