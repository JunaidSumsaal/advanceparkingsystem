import json
import logging
import requests
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from celery import shared_task
from .models import Notification, PushSubscription, Notification as NotificationModel
from .utils import send_web_push
from .emailer import send_email_notification
from .realtime import broadcast_ws_to_user

logger = logging.getLogger(__name__)

User = get_user_model()

def _persist_and_payload(user_id, title, body, type_="general", extra=None):
    notif = NotificationModel.objects.create(
        user_id=user_id, title=title, body=body, type=type_
    )
    payload = {
        "id": notif.id,
        "title": title,
        "body": body,
        "type": type_,
        "sent_at": notif.sent_at.isoformat(),
        "extra": extra or {},
    }
    return notif, payload

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_notification_async(self, user_id, title, body, type_="general", extra=None):
    notif, payload = _persist_and_payload(user_id, title, body, type_, extra)
    try:
        broadcast_ws_to_user(user_id, payload)
    except Exception:
        pass

    delivered = False
    subs = PushSubscription.objects.filter(user_id=user_id)
    for sub in subs:
        ok, err = send_web_push(sub, payload)
        if ok:
            delivered = True
        else:
            pass

    user = User.objects.filter(id=user_id).only("email").first()
    if user and user.email:
        try:
            send_email_notification(user.email, title, body)
            delivered = True or delivered
        except Exception:
            pass

    notif.delivered = delivered
    notif.status = "sent" if delivered else "pending"
    notif.save()
    return {"id": notif.id, "delivered": delivered}

@shared_task(rate_limit="30/m")
def booking_reminder_task(booking_id):
    from parking.models import Booking

    try:
        b = Booking.objects.select_related("user", "parking_spot").get(id=booking_id)
    except Booking.DoesNotExist:
        print(f"[booking_reminder_task] Booking {booking_id} does not exist. Skipping reminder.")
        return
    
    if b.user_id is None or b.parking_spot is None:
        print(f"[booking_reminder_task] Booking {booking_id} has missing user or spot. Skipping.")
        return None

    title = "⏰ Booking Reminder"
    body = f"Your booking for {b.parking_spot.name} is active. End it when you leave."

    # Use .delay() to send notification asynchronously
    return send_notification_async.delay(b.user_id, title, body, "booking_reminder")

@shared_task
def daily_digest_for_provider(provider_id):
    from parking.models import ParkingFacility, ParkingSpot, Booking
    active = Booking.objects.filter(parking_spot__provider_id=provider_id, is_active=True).count()
    body = f"Daily digest: {active} active bookings."
    return send_notification_async.delay(provider_id, "📊 Daily Digest", body, "general")


@shared_task(rate_limit="60/m")  # optional rate limit
def send_pending_notifications(batch_size=50):
    pending = Notification.objects.filter(
        delivered=False, status="pending"
    )[:batch_size]

    for n in pending:
        subs = PushSubscription.objects.filter(user=n.user)

        if not subs.exists():
            n.status = "no_subscriber"
            n.save(update_fields=["status"])
            continue

        delivered = False

        for sub in subs:
            try:
                resp = requests.post(
                    sub.endpoint,
                    data=json.dumps({
                        "title": n.title,
                        "body": n.body,
                        "type": n.type,
                    }),
                    headers={"Content-Type": "application/json"},
                    timeout=5,
                )

                if resp.status_code == 201 or resp.status_code == 200:
                    delivered = True
                else:
                    logger.warning(f"Push failed [{resp.status_code}] for sub {sub.id}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Push error for sub {sub.id}: {e}")
                n.status = f"error:{type(e).__name__}"

        if delivered:
            with transaction.atomic():
                n.delivered = True
                n.status = "sent"
                n.sent_at = timezone.now()
                n.save(update_fields=["delivered", "status", "sent_at"])
        else:
            n.save(update_fields=["status"])
