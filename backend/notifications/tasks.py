import json
import logging
import requests
from django.utils import timezone
from django.db import transaction
from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Notification, PushSubscription
from .utils import broadcast_ws_to_user, send_web_push
from .emailer import send_email_notification

logger = logging.getLogger(__name__)
User = get_user_model()

import json
import requests
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Notification, PushSubscription
from .utils import broadcast_ws_to_user, send_web_push
from .emailer import send_email_notification

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

    # WebSocket broadcast (always serializer-based)
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
    try:
        b = Booking.objects.select_related("user", "parking_spot").get(id=booking_id)
    except Booking.DoesNotExist:
        return

    if not b.user_id or not b.parking_spot:
        return None

    title = "⏰ Booking Reminder"
    body = f"Your booking for {b.parking_spot.name} is active. End it when you leave."
    send_notification_async.delay(b.user_id, title, body, "booking_reminder")


@shared_task
def daily_digest_for_provider(provider_id):
    from parking.models import Booking
    active = Booking.objects.filter(parking_spot__provider_id=provider_id, is_active=True).count()
    body = f"Daily digest: {active} active bookings."
    return send_notification_async.delay(provider_id, "📊 Daily Digest", body, "general")


@shared_task(rate_limit="60/m")
def send_pending_notifications(batch_size=50):
    pending = Notification.objects.filter(delivered=False, status="pending")[:batch_size]

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
                    data=json.dumps({"title": n.title, "body": n.body, "type": n.type}),
                    headers={"Content-Type": "application/json"},
                    timeout=5,
                )
                if resp.status_code in [200, 201]:
                    delivered = True
            except requests.exceptions.RequestException as e:
                logger.error(f"Push error for sub {sub.id}: {e}")

        if delivered:
            with transaction.atomic():
                n.delivered = True
                n.status = "sent"
                n.sent_at = timezone.now()
                n.save(update_fields=["delivered", "status", "sent_at"])
        else:
            n.save(update_fields=["status"])
