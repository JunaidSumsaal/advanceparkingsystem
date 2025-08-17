from datetime import timezone
from django.utils.timezone import now, timedelta
from parking.ml.predict_service import predict_for_spots
from .models import Booking, ParkingSpot, SpotPredictionLog
from notifications.utils import send_push_notification, log_notification_event
from notifications.models import PushSubscription
from celery import shared_task

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

@shared_task
def run_spot_predictions():
    spots = ParkingSpot.objects.filter(is_available=True)
    if not spots.exists():
        return "No spots available"

    predictions = predict_for_spots(spots)
    saved = 0
    for p in predictions:
        SpotPredictionLog.objects.create(
            parking_spot=p["spot"],
            probability=p["probability"],
            predicted_for_time=timezone.now() + timedelta(minutes=15),
            model_version="v1"
        )
        saved += 1
    return f"Saved {saved} predictions"
