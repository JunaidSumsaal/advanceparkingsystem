import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from parking.models import ParkingFacility, ParkingSpot, SpotAvailabilityLog, Booking, SpotPredictionLog
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = "Seed database with users, facilities, spots, availability logs, bookings, notifications, and AI predictions"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🚀 Seeding data..."))

        # Clean existing
        Booking.objects.all().delete()
        SpotAvailabilityLog.objects.all().delete()
        ParkingSpot.objects.all().delete()
        ParkingFacility.objects.all().delete()
        Notification.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        
        # --- Admin
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser '{admin_username}' created successfully."))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists. No action taken."))

        # --- Users
        providers = [
            User.objects.create_user(
                username=f"provider{i}",
                email=f"provider{i}@example.com",
                password="password123",
                role="provider"
            )
            for i in range(10)
        ]
        self.stdout.write(self.style.SUCCESS(f"Provers added '{len(providers)}' created successfully."))
        attendants = [
            User.objects.create_user(
                username=f"attendant{i}",
                email=f"attendant{i}@example.com",
                password="password123",
                role="attendant"
            )
            for i in range(40)
        ]
        self.stdout.write(self.style.SUCCESS(f"Attendants added '{len(attendants)}' created successfully."))
        customers = [
            User.objects.create_user(
                username=f"driver{i}",
                email=f"driver{i}@example.com",
                password="password123",
                role="driver"
            )
            for i in range(500)
        ]
        self.stdout.write(self.style.SUCCESS(f"Provers added '{len(customers)}' created successfully."))
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
            # Archive some facilities
            if random.random() < 0.2:  # 20% chance of archiving
                facility.is_active = False
                facility.save()
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
                # Archive some spots
                if random.random() < 0.2:  # 20% chance of archiving
                    spot.is_active = False
                    spot.save()
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
                    booking = Booking.objects.create(
                        user=random.choice(customers),
                        parking_spot=spot,
                        start_time=current_time,
                        is_active=random.choice([True, False]),
                        total_price=spot.price_per_hour * 2  # Example total price
                    )

                current_time += timedelta(minutes=30)
        self.stdout.write(self.style.SUCCESS("✅ Logs & Bookings created"))

        # --- AI Predictions
        for spot in spots:
            current_time = timezone.now() - timedelta(days=7)
            for i in range(100):  # 100 AI prediction logs
                prediction = SpotPredictionLog.objects.create(
                    parking_spot=spot,
                    predicted_for_time=current_time,
                    probability=random.uniform(0.5, 1.0),
                    model_version="v1.0",
                )
                
                # Archive some prediction logs
                if random.random() < 0.2:  # 20% chance of archiving
                    prediction.is_active = False
                    prediction.save()

                current_time += timedelta(hours=1)
        self.stdout.write(self.style.SUCCESS("✅ AI Prediction logs created"))

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
