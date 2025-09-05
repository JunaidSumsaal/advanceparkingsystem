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
def send_notification_async(
    self,
    user_id,
    title,
    body,
    type_="general",
    extra=None,
    notification_id=None,
    is_public=False,
):
    User = get_user_model()
    user = User.objects.filter(id=user_id).only(
        "id", "email", "latitude", "longitude").first()
    if not user:
        return None

    # Distance filter for public notifications
    if is_public and extra:
        lat, lng = extra.get("lat"), extra.get("lng")
        if lat and lng and user.latitude and user.longitude:
            distance = get_distance_km(
                (lat, lng), (user.latitude, user.longitude))
            if distance is None or distance > 10:
                return None
            spot_name = extra.get("spot_name", "Parking Spot")
            body += f"\n📍 {spot_name} is {distance:.1f} km away."

    # Create child notification for this user
    notif = Notification.objects.create(
        user_id=user_id,
        parent_id=notification_id,
        title=title,
        body=body,
        type=type_,
        status="pending",
        delivered=False,
        extra=extra or {},
    )

    delivered = False

    # WebSocket
    try:
        broadcast_ws_to_user(user_id, notif)
    except Exception:
        pass

    # Push Subscriptions
    for sub in PushSubscription.objects.filter(user_id=user_id):
        try:
            ok, _ = send_web_push(
                sub, {"title": title, "body": body, "type": type_})
            if ok:
                delivered = True
        except Exception as e:
            logger.error(f"Push error for sub {sub.id}: {e}")

    # Email fallback
    if user.email and not delivered:
        try:
            send_email_notification(user.email, title, body)
            delivered = True
        except Exception as e:
            logger.error(f"Email error for {user.email}: {e}")

    # Finalize child status
    notif.delivered = delivered
    notif.status = "sent" if delivered else "failed"
    notif.sent_at = timezone.now()
    notif.save(update_fields=["delivered", "status", "sent_at"])

    # Update parent status if all children are resolved
    if notification_id:
        unresolved = Notification.objects.filter(
            parent_id=notification_id, status="pending"
        ).exists()
        if not unresolved:
            Notification.objects.filter(
                id=notification_id).update(status="completed")

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
        delivered=False, status="pending"
    ).select_related("user")[:batch_size]

    for n in pending:
        if n.is_public:
            users = User.objects.exclude(latitude=None, longitude=None)
        else:
            users = [n.user] if n.user else []

        for user in users:
            send_notification_async.delay(
                user.id,
                n.title,
                n.body,
                n.type,
                extra=n.extra or {},
                notification_id=n.id,
                is_public=n.is_public,
            )

        n.status = "dispatched"
        n.save(update_fields=["status"])

