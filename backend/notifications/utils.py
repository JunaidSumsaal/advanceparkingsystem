from django.conf import settings
from .models import PushSubscription, Notification
from django.core.mail import send_mail
import json, requests
from pywebpush import webpush, WebPushException

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
            send_mail(
                title,
                message,
                'no-reply@smartparking.com',
                [sub.user.email],
                fail_silently=True
            )

def send_push_notification(subscription, title, body):
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
            vapid_claims={"sub": "mailto:admin@example.com"}
        )
        Notification.objects.create(user=subscription.user, title=title, body=body, success=True)
    except WebPushException as e:
        Notification.objects.create(user=subscription.user, title=title, body=body, success=False)
