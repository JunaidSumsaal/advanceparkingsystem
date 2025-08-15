from django.core.management.base import BaseCommand
from parking.ml import train

class Command(BaseCommand):
    help = "Train the parking spot availability prediction model and save it."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting model training..."))
        try:
            train.train_and_save()
            self.stdout.write(self.style.SUCCESS("Model training completed successfully."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during training: {e}"))
