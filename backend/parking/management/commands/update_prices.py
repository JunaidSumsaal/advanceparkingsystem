from django.core.management.base import BaseCommand
from parking.pricing import update_dynamic_prices

class Command(BaseCommand):
    help = "Recalculate dynamic prices for all spots"

    def handle(self, *args, **options):
        updated = update_dynamic_prices()
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} spots"))
