from django.core.management.base import BaseCommand
from django.utils import timezone
from parking.models import ParkingSpot, SpotPredictionLog
from parking.ml.predict_service import predict_for_spots
from datetime import timedelta

class Command(BaseCommand):
    help = "Run periodic predictions for available parking spots"

    def handle(self, *args, **kwargs):
        self.stdout.write("Running spot predictions...")

        # Select active spots only
        spots = ParkingSpot.objects.filter(is_available=True)
        if not spots.exists():
            self.stdout.write("No available spots found.")
            return

        predictions = predict_for_spots(spots)

        saved_count = 0
        for p in predictions:
            SpotPredictionLog.objects.create(
                parking_spot=p["spot"],
                probability=p["probability"],
                predicted_for_time=timezone.now() + timedelta(minutes=15),
                model_version="v1"
            )
            saved_count += 1

        self.stdout.write(self.style.SUCCESS(f"Saved {saved_count} predictions."))
