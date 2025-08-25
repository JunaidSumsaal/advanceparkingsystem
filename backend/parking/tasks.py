from .ml.train import train_and_save
from .ml.eval import evaluate_model
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from .pricing import update_dynamic_prices
from .models import Booking, ParkingSpot, SpotPredictionLog
from .prediction_service import compute_probability
from notifications.tasks import send_notification_async

@shared_task
def recalc_dynamic_prices():
    return update_dynamic_prices()

@shared_task
def generate_archive_report_task(period="daily"):
    call_command("generate_archive_report", period=period)

@shared_task
def run_spot_predictions():
    spots = ParkingSpot.objects.filter(is_available=True)
    if not spots.exists():
        return "No spots available"

    saved = 0
    pred_for = timezone.now() + timedelta(minutes=15)
    for spot in spots:
        p = compute_probability(spot)
        SpotPredictionLog.objects.create(
            parking_spot=spot,
            probability=p,
            predicted_for_time=pred_for,
            model_version="v1",
        )
        saved += 1
    return f"Saved {saved} predictions"

@shared_task
def send_booking_expiry_reminders():
    now = timezone.now()
    soon = now + timedelta(minutes=10)
    qs = Booking.objects.filter(is_active=True, end_time__lte=soon, end_time__gte=now)
    for b in qs.select_related("parking_spot", "user"):
        send_notification_async.delay(
            b.user_id,
            "⏰ Booking Expiring Soon",
            f"Your booking for {b.parking_spot.name} will expire in 10 minutes.",
            "booking_reminder",
        )



@shared_task
def retrain_spot_predictor():
    return train_and_save()

@shared_task
def evaluate_spot_predictor():
    return evaluate_model()
