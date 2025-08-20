# parking/management/commands/generate_archive_report.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Sum
from parking.models import ArchiveReport, ParkingFacility, ParkingSpot, Booking
from notifications.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = "Generate daily/weekly archive reports for providers & superadmins"

    def add_arguments(self, parser):
        parser.add_argument(
            "--period", type=str, choices=["daily", "weekly"], default="daily"
        )

    def handle(self, *args, **options):
        period = options["period"]
        now = timezone.now()

        # Provider-specific reports
        providers = User.objects.filter(role="provider")
        for provider in providers:
            facilities = ParkingFacility.objects.filter(provider=provider)
            spots = ParkingSpot.objects.filter(facility__in=facilities)
            bookings = Booking.objects.filter(parking_spot__in=spots)

            report = {
                "facilities": facilities.count(),
                "spots": spots.count(),
                "active_bookings": bookings.filter(is_active=True).count(),
                "ended_bookings": bookings.filter(is_active=False).count(),
            }

            Notification.objects.create(
                user=provider,
                title=f"{period.title()} Report",
                body=f"""
                📊 {period.title()} Summary
                Facilities: {report['facilities']}
                Spots: {report['spots']}
                Active Bookings: {report['active_bookings']}
                Ended Bookings: {report['ended_bookings']}
                """,
                type="general",
                delivered=True,
                status="sent",
            )

            ArchiveReport.objects.create(
                user=provider,
                title=f"{period.title()} Report",
                body=f"Facilities: {report['facilities']} ...",
                period=period
            )

        # Superadmin global report
        superadmins = User.objects.filter(is_superuser=True)
        all_facilities = ParkingFacility.objects.count()
        all_spots = ParkingSpot.objects.count()
        all_active_bookings = Booking.objects.filter(is_active=True).count()
        all_ended_bookings = Booking.objects.filter(is_active=False).count()

        for sa in superadmins:
            Notification.objects.create(
                user=sa,
                title=f"Global {period.title()} Report",
                body=f"""
                🌍 Global {period.title()} Summary
                Facilities: {all_facilities}
                Spots: {all_spots}
                Active Bookings: {all_active_bookings}
                Ended Bookings: {all_ended_bookings}
                """,
                type="general",
                delivered=True,
                status="sent",
            )

            ArchiveReport.objects.create(
                user=sa,
                title=f"{period.title()} Report",
                body=f"Facilities: {report['facilities']} ...",
                period=period
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{period.title()} reports generated for providers & superadmins")
        )
