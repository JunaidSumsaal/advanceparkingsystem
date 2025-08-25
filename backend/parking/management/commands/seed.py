import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from accounts.models import AuditLog, NewsletterSubscription
from parking.models import ArchiveReport, AttendantAssignmentLog, ModelEvaluationLog, ParkingFacility, ParkingSpot, SpotAvailabilityLog, Booking, SpotPredictionLog, SpotPriceLog, SpotReview
from notifications.models import Notification, NotificationPreference
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
        self.stdout.write(self.style.WARNING("Cleaning existing data..."))
        # Delete dependent tables first
        AuditLog.objects.all().delete()
        Notification.objects.all().delete()
        NewsletterSubscription.objects.all().delete()
        NotificationPreference.objects.all().delete()

        # Then delete other models
        Booking.objects.all().delete()
        SpotReview.objects.all().delete()
        SpotAvailabilityLog.objects.all().delete()
        SpotPredictionLog.objects.all().delete()
        SpotPriceLog.objects.all().delete()
        ArchiveReport.objects.all().delete()
        ModelEvaluationLog.objects.all().delete()
        AttendantAssignmentLog.objects.all().delete()
        ParkingSpot.objects.all().delete()
        ParkingFacility.objects.all().delete()

        # Finally, delete users
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
            self.stdout.write(self.style.SUCCESS(
                f"Superuser '{admin_username}' created successfully."))
        else:
            self.stdout.write(self.style.WARNING(
                "Superuser already exists. No action taken."))

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
        self.stdout.write(self.style.SUCCESS(
            f"Providers added '{len(providers)}' created successfully."))
        attendants = [
            User.objects.create_user(
                username=f"attendant{i}",
                email=f"attendant{i}@example.com",
                password="password123",
                role="attendant"
            )
            for i in range(40)
        ]
        self.stdout.write(self.style.SUCCESS(
            f"Attendants added '{len(attendants)}' created successfully."))
        customers = [
            User.objects.create_user(
                username=f"driver{i}",
                email=f"driver{i}@example.com",
                password="password123",
                role="driver"
            )
            for i in range(500)
        ]
        self.stdout.write(self.style.SUCCESS(
            f"Driver added '{len(customers)}' created successfully."))
        self.stdout.write(self.style.SUCCESS("Users created"))

        # --- Create User-related preferences and subscriptions ---
        self.stdout.write(self.style.WARNING("Creating user preferences..."))
        for user in customers + providers + attendants:
            NotificationPreference.objects.create(
                user=user, push_enabled=random.choice([True, False]), email_enabled=random.choice([True, False]), newsletter_enabled=random.choice([True, False]))
            NewsletterSubscription.objects.create(
                user=user, email=user.email, subscribed=random.choice([True, False]))
        self.stdout.write(self.style.SUCCESS(
            "Email preferences and newsletter subscriptions created."))

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
            assigned_attendants = random.sample(attendants, k=2)
            facility.attendants.set(assigned_attendants)
            for attendant in assigned_attendants:
                AttendantAssignmentLog.objects.create(
                    facility=facility,
                    attendant=attendant,
                    performed_by=provider,
                    action='assigned'
                )
            # Archive some facilities
            if random.random() < 0.2:  # 20% chance of archiving
                facility.is_active = False
                facility.save()
            facilities.append(facility)
        self.stdout.write(self.style.SUCCESS("Facilities created"))

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
        self.stdout.write(self.style.SUCCESS("Spots created"))

        # --- Logs & Bookings
        for spot in spots:
            current_time = timezone.now() - timedelta(days=7)
            is_available = True

            for i in range(300):  # 300 log entries per spot
                SpotAvailabilityLog.objects.create(
                    parking_spot=spot,
                    timestamp=timezone.now() - timedelta(minutes=60 - i),
                    is_available=random.choice([True, False]),
                    changed_by=None
                )

                # Create a booking only when spot is not available
                if not is_available and random.random() < 0.3:
                    booking_user = random.choice(customers)
                    booking = Booking.objects.create(
                        user=booking_user,
                        parking_spot=spot,
                        start_time=timezone.now() - timedelta(minutes=60 - i),
                        is_active=random.choice([True, False]),
                        total_price=spot.price_per_hour * 2
                    )

                    # Add a review for some completed bookings
                    if not booking.is_active and random.random() < 0.5:
                        SpotReview.objects.update_or_create(
                            user=booking.user,
                            parking_spot=spot,
                            defaults={
                                "rating": random.randint(1, 5),
                                "comment": fake.text(max_nb_chars=100),
                            }
                        )
                current_time += timedelta(minutes=30)
        self.stdout.write(self.style.SUCCESS("Logs & Bookings created"))

        # --- AI Predictions
        for spot in spots:
            for i in range(100):  # 100 AI prediction logs
                prediction = SpotPredictionLog.objects.create(
                    parking_spot=spot,
                    predicted_for_time=timezone.now() - timedelta(minutes=60 - i),
                    probability=random.uniform(0.5, 1.0),
                    model_version="v1.0",
                )

                # Archive some prediction logs
                if random.random() < 0.4:  # 40% chance of archiving
                    prediction.is_active = False
                    prediction.save()

                current_time += timedelta(hours=1)
        for _ in range(5):
            ModelEvaluationLog.objects.create(
                auc_score=random.uniform(0.7, 0.95),
                brier_score=random.uniform(0.05, 0.3),
                tolerance_seconds=random.choice([60, 120, 300]),
                evaluated_at=timezone.now() - timedelta(days=random.randint(1, 60))
            )
        self.stdout.write(self.style.SUCCESS("AI Prediction logs created"))

        # --- Create Spot Price and Archive Reports ---
        self.stdout.write(self.style.WARNING(
            "Creating spot price and archive reports..."))
        for spot in random.sample(spots, k=50):
            old_price = spot.price_per_hour
            new_price = old_price * random.uniform(0.8, 1.2)
            SpotPriceLog.objects.create(
                parking_spot=spot,
                old_price=old_price,
                new_price=new_price,
                updated_at=timezone.now() - timedelta(hours=random.randint(1, 24))
            )
            spot.price_per_hour = new_price
            spot.save()
        for user in random.sample(providers, k=3):
            ArchiveReport.objects.create(
                user=user,
                title=f"{random.choice(['Daily', 'Weekly'])} Archived Data Report",
                body=f"This report details archived data for {user.company_name or user.username}.",
                period=random.choice(["daily", "weekly"]),
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
        self.stdout.write(self.style.SUCCESS(
            "Spot price and archive reports created."))

        # --- Create Audit Logs ---
        self.stdout.write(self.style.WARNING("Creating audit logs..."))
        all_users = list(customers) + list(providers) + list(attendants)
        for _ in range(200):
            user = random.choice(all_users)
            action = random.choice(["login", "booking_create", "spot_update",
                                   "facility_update", "attendant_assignment", "notification_sent"])
            AuditLog.objects.create(
                user=user,
                action=action,
                description=f"User {user.username} performed the {action} action.",
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                timestamp=timezone.now() - timedelta(minutes=random.randint(1, 1440))
            )
        self.stdout.write(self.style.SUCCESS("Audit logs created."))

        # --- Notifications
        for cust in customers:
            Notification.objects.create(
                user=cust,
                title="Welcome!",
                body="Thanks for signing up. Get ready to find parking easily.",
                type="general"
            )
        self.stdout.write(self.style.SUCCESS("Notifications created"))

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully"))
        self.stdout.write(self.style.SUCCESS(
            "Database seeded with test data!"))
