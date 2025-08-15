from django.core.management.base import BaseCommand
from parking.ml import eval as eval_module

class Command(BaseCommand):
    help = "Evaluate the parking spot prediction model using historical logs."

    def add_arguments(self, parser):
        parser.add_argument(
            '--tolerance',
            type=int,
            default=120,
            help="Tolerance in seconds when matching predictions to actual availability (default: 120)"
        )

    def handle(self, *args, **options):
        tolerance = options['tolerance']
        self.stdout.write(self.style.NOTICE(
            f"Starting evaluation with tolerance={tolerance} seconds..."
        ))

        try:
            eval_module.evaluate_predictions(tolerance_seconds=tolerance)
            self.stdout.write(self.style.SUCCESS("Evaluation completed successfully."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during evaluation: {e}"))
