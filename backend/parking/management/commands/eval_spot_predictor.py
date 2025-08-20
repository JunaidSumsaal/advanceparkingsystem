from django.core.management.base import BaseCommand
from parking.ml.eval import evaluate_model

class Command(BaseCommand):
    help = "Evaluate the trained parking spot predictor model"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🚀 Starting model evaluation..."))
        try:
            evaluate_model()
            self.stdout.write(self.style.SUCCESS("Evaluation completed successfully"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during evaluation: {e}"))
