from celery import shared_task
from django.conf import settings
import json
import requests
from pywebpush import webpush, WebPushException
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .emailer import send_email_notification
from .models import NotificationPreference, NotificationTemplate, PushSubscription, Notification


def push_realtime_notification(user, event_type, context):
    template = NotificationTemplate.objects.filter(
        event_type=event_type).first()
    rendered = template.render(context) if template else {
        "title": f"{event_type}",
        "body": str(context),
    }

    notif = Notification.objects.create(
        user=user,
        title=rendered["title"],
        body=rendered["body"],
        type=event_type,
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "data": {
                "id": notif.id,
                "title": notif.title,
                "body": notif.body,
                "type": notif.type,
                "sent_at": str(notif.sent_at),
            },
        },
    )

    return notif


def send_spot_available_notification(spot):
    # sourcery skip: do-not-use-bare-except
    subscriptions = PushSubscription.objects.all()
    title = "Parking Spot Available!"
    message = f"{spot.name} is now free. Tap for navigation."

    for sub in subscriptions:
        Notification.objects.create(
            user=sub.user,
            title=title,
            message=message,
            type="spot-available",
            delivered=True
        )

        payload = {"title": title, "body": message}
        try:
            requests.post(sub.endpoint, data=json.dumps(payload))
        except:
            pass

        # Send email fallback
        if hasattr(sub.user, 'emailpreference') and sub.user.emailpreference.receive_emails:
            send_email_notification(
                sub.user.email,
                title,
                message,
            )


def send_web_push(subscription, title, body):
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth
                }
            },
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_CLAIM_SUB},
            ttl=60  # Time to live in seconds
        )
        Notification.objects.create(
            user=subscription.user, title=title, body=body, success=True, status='delivered')
    except WebPushException as e:
        Notification.objects.create(
            user=subscription.user, title=title, body=body, success=False, status='failed')


@shared_task
def send_notification_task(notification_id):
    try:
        notif = Notification.objects.get(id=notification_id)
        prefs = NotificationPreference.objects.get(user=notif.user)

        if prefs.email_enabled:
            send_email_notification(
                notif.user.email,
                notif.title,
                notif.body,
            )

        if prefs.push_enabled:
            subs = PushSubscription.objects.filter(user=notif.user)
            for sub in subs:
                send_web_push(sub, notif.title, notif.body)

        notif.delivered = True
        notif.save()
    except Exception as e:
        print(f"Error sending notification: {e}")


def notify_user(user, event_type, context):
    try:
        template = NotificationTemplate.objects.get(event_type=event_type)
        rendered = template.render(context)
    except NotificationTemplate.DoesNotExist:
        rendered = {
            "title": f"Notification: {event_type}",
            "body": str(context),
        }

    notification = Notification.objects.create(
        user=user,
        title=rendered["title"],
        body=rendered["body"],
        type=event_type,
    )
    notification.save()
    send_notification_task.delay(notification.id)


def log_notification_event(user, title, message, n_type, status):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=n_type,
        status=status
    )


@shared_task
def send_newsletters():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(
        notificationpreference__newsletter_enabled=True)

    for user in users:
        send_email_notification(
            user.email,
            "AdvanceParkingSystem Updates",
            "Here are the latest updates about facilities, spots, and offers.",
        )
