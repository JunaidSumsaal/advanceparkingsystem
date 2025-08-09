from django.utils.timezone import now, timedelta
from .models import Booking
from notifications.utils import send_push_notification, log_notification_event
from notifications.models import PushSubscription

def send_booking_reminders():
    upcoming_bookings = Booking.objects.filter(
        is_active=True,
        end_time__lte=now() + timedelta(minutes=10),
        end_time__gte=now()
    )
    for booking in upcoming_bookings:
        subscriptions = PushSubscription.objects.filter(user=booking.user)
        for sub in subscriptions:
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
            }
            status = "sent" if send_push_notification(
                subscription_info,
                "Booking Expiring Soon",
                f"Your booking for {booking.parking_spot.name} will expire in 10 minutes."
            ) else "failed"
            log_notification_event(booking.user, "Booking Expiring Soon",
                                  f"Your booking for {booking.parking_spot.name} will expire in 10 minutes.",
                                  "booking_reminder", status)
