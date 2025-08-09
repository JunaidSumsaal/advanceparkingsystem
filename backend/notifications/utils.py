from .models import PushSubscription, Notification
from django.core.mail import send_mail
import json, requests

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

