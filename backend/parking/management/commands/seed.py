from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from parking.models import ParkingFacility, ParkingSpot, SpotAvailabilityLog, Booking
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = "Seed database with users, facilities, spots, availability logs, bookings, and notifications"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🚀 Seeding data..."))

        # Clean existing
        Booking.objects.all().delete()
        SpotAvailabilityLog.objects.all().delete()
        ParkingSpot.objects.all().delete()
        ParkingFacility.objects.all().delete()
        Notification.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # --- Users
        providers = [
            User.objects.create_user(
                username=f"provider{i}",
                email=f"provider{i}@example.com",
                password="password123",
                role="provider"
            )
            for i in range(3)
        ]
        attendants = [
            User.objects.create_user(
                username=f"attendant{i}",
                email=f"attendant{i}@example.com",
                password="password123",
                role="attendant"
            )
            for i in range(3)
        ]
        customers = [
            User.objects.create_user(
                username=f"customer{i}",
                email=f"customer{i}@example.com",
                password="password123",
                role="customer"
            )
            for i in range(5)
        ]
        self.stdout.write(self.style.SUCCESS("✅ Users created"))

        # --- Facilities
        facilities = []
        for provider in providers:
            facility = ParkingFacility.objects.create(
                provider=provider,
                name=fake.company(),
                capacity=random.randint(10, 50),
                latitude=fake.latitude(),
                longitude=fake.longitude(),
                address=fake.address(),
            )
            facility.attendants.set(random.sample(attendants, k=2))
            facilities.append(facility)
        self.stdout.write(self.style.SUCCESS("✅ Facilities created"))

        # --- Spots
        spots = []
        for facility in facilities:
            for i in range(random.randint(5, 10)):
                spot = ParkingSpot.objects.create(
                    facility=facility,
                    name=f"Spot-{facility.id}-{i}",
                    latitude=fake.latitude(),
                    longitude=fake.longitude(),
                    spot_type=random.choice(["public", "private"]),
                    price_per_hour=random.choice([1.5, 2.0, 3.0, 5.0]),
                    is_available=True,
                    provider=facility.provider,
                    created_by=facility.provider,
                )
                spots.append(spot)
        self.stdout.write(self.style.SUCCESS("✅ Spots created"))

        # --- Logs & Bookings
        for spot in spots:
            current_time = timezone.now() - timedelta(days=7)
            is_available = True

            for i in range(200):  # 200 log entries
                # Force variability
                if i % 5 == 0 or random.random() < 0.2:
                    is_available = not is_available

                SpotAvailabilityLog.objects.create(
                    parking_spot=spot,
                    timestamp=current_time,
                    is_available=is_available,
                    changed_by=None
                )

                if not is_available and random.random() < 0.3:
                    Booking.objects.create(
                        user=random.choice(customers),
                        parking_spot=spot,
                        start_time=current_time,
                        is_active=random.choice([True, False])
                    )

                current_time += timedelta(minutes=30)
        self.stdout.write(self.style.SUCCESS("✅ Logs & Bookings created"))

        # --- Notifications
        for cust in customers:
            Notification.objects.create(
                user=cust,
                title="Welcome!",
                body="Thanks for signing up. Get ready to find parking easily.",
                type="general"
            )
        self.stdout.write(self.style.SUCCESS("✅ Notifications created"))

        self.stdout.write(self.style.SUCCESS("🎉 Seeding completed successfully"))
        self.stdout.write(self.style.SUCCESS("🚀 Database seeded with test data!"))