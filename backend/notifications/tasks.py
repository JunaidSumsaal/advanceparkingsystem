import json
import requests
from django.utils import timezone
from django.contrib.auth import get_user_model
from celery import shared_task
from .models import Notification, PushSubscription, Notification as NotificationModel
from .utils import send_web_push
from .emailer import send_email_notification
from .realtime import broadcast_ws_to_user

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
    b = Booking.objects.select_related("user", "parking_spot").get(id=booking_id)
    title = "⏰ Booking Reminder"
    body = f"Your booking for {b.parking_spot.name} is active. End it when you leave."
    return send_notification_async.delay(b.user_id, title, body, "booking_reminder")

@shared_task
def daily_digest_for_provider(provider_id):
    from parking.models import ParkingFacility, ParkingSpot, Booking
    active = Booking.objects.filter(parking_spot__provider_id=provider_id, is_active=True).count()
    body = f"Daily digest: {active} active bookings."
    return send_notification_async.delay(provider_id, "📊 Daily Digest", body, "general")


@shared_task
def send_pending_notifications():
    pending = Notification.objects.filter(delivered=False, status="pending")[:50]
    for n in pending:
        subs = PushSubscription.objects.filter(user=n.user)
        if not subs.exists():
            n.status = "no_subscriber"
            n.save()
            continue

        for sub in subs:
            try:
                requests.post(sub.endpoint, data=json.dumps({
                    "title": n.title,
                    "body": n.body,
                    "type": n.type,
                }))
                n.delivered = True
                n.status = "sent"
                n.sent_at = timezone.now()
                n.save()
            except Exception as e:
                n.status = f"error:{e}"
                n.save()
