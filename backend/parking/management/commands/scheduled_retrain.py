from django.core.management.base import BaseCommand
from parking.ml.train import train_and_save

class Command(BaseCommand):
    help = "Scheduled retraining of spot prediction model"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting scheduled retraining...")
        try:
            train_and_save()
            self.stdout.write(self.style.SUCCESS("Retraining completed successfully"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Retraining failed: {e}"))
