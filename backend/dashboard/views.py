from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from accounts.utils import IsAdminOrSuperuser, IsAttendant, IsDriver, IsProviderOrAdmin
from parking.models import ParkingSpot, SpotPredictionLog, SpotAvailabilityLog
from sklearn.metrics import precision_score, recall_score, f1_score
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from parking.models import Booking, ParkingSpot, ParkingFacility
from accounts.models import User
from django.db.models import Count, Avg
from django.db.models.functions import TruncDay
from .utils import get_booking_trends, get_facility_metrics
from django.db.models import Count, Avg, Sum
from django.utils import timezone


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperuser]

    def get(self, request):
        user = request.user
        if not user.is_authenticated or user.role not in ['admin', 'superuser']:
            return Response({"error": "Not authorized"}, status=403)

        # Totals
        total_users = User.objects.count()
        total_facilities = ParkingFacility.objects.count()
        total_spots = ParkingSpot.objects.count()
        total_bookings = Booking.objects.count()

        # Breakdown of users by role
        user_breakdown = (
            User.objects.values("role")
            .annotate(count=Count("id"))
            .order_by("role")
        )

        # Revenue insights
        revenue_total = Booking.objects.aggregate(
            total=Sum("total_price"))["total"] or 0
        revenue_per_facility = (
            Booking.objects.values("parking_spot__facility__name")
            .annotate(total=Sum("total_price"))
            .order_by("-total")
        )

        # Recent activity
        recent_bookings = Booking.objects.select_related("user", "parking_spot") \
            .order_by("-start_time")[:5] \
            .values("id", "user__email", "parking_spot__facility__name", "start_time")

        recent_users = User.objects.order_by("-date_joined")[:5] \
            .values("id", "email", "role", "date_joined")

        # AI prediction stats (optional)
        prediction_logs = SpotPredictionLog.objects.count()
        availability_logs = SpotAvailabilityLog.objects.count()

        data = {
            "total_users": total_users,
            "total_facilities": total_facilities,
            "total_spots": total_spots,
            "total_bookings": total_bookings,
            "user_breakdown": list(user_breakdown),
            "booking_trends": get_booking_trends(),
            "facility_metrics": get_facility_metrics(),
            "revenue": {
                "total": revenue_total,
                "by_facility": list(revenue_per_facility),
            },
            "recent_activity": {
                "bookings": list(recent_bookings),
                "users": list(recent_users),
            },
            "ai_stats": {
                "prediction_logs": prediction_logs,
                "availability_logs": availability_logs,
            },
        }
        return Response(data)


class DriverDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsDriver]

    def get(self, request):
        user = request.user
        bookings = Booking.objects.filter(user=user)
        active_bookings = bookings.filter(is_active=True)
        past_bookings = bookings.filter(is_active=False)

        total_spending = bookings.aggregate(total_spending=Sum('total_price'))[
            'total_spending'] or 0
        upcoming_bookings = active_bookings.filter(
            start_time__gt=timezone.now())
        recent_activity = active_bookings.order_by('-start_time')[:5]

        return Response({
            "active_bookings": active_bookings.count(),
            "past_bookings": past_bookings.count(),
            "total_spending": total_spending,
            "upcoming_bookings": upcoming_bookings.values('parking_spot__facility__name', 'start_time', 'end_time'),
            "recent_activity": recent_activity.values('id', 'user__email', 'parking_spot__facility__name', 'start_time')
        })


class AttendantDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAttendant]

    def get(self, request):
        facilities = ParkingFacility.objects.filter(attendants=request.user)
        spots = ParkingSpot.objects.filter(facility__in=facilities)
        bookings = Booking.objects.filter(user=request.user)

        active_spots = spots.filter(is_available=True).count()
        occupied_spots = spots.filter(is_available=False).count()

        recent_bookings = bookings.filter(
            parking_spot__in=spots).order_by('-start_time')[:5]
        
        active_bookings = bookings.filter(is_active=True)
        past_bookings = bookings.filter(is_active=False)

        total_spending = bookings.aggregate(total_earnings=Sum('total_price'))['total_earnings'] or 0
        upcoming_bookings = active_bookings.filter(start_time__gt=timezone.now())
        recent_activity = active_bookings.order_by('-start_time')[:5]

        facility_metrics = []
        for facility in facilities:
            total_spots = ParkingSpot.objects.filter(facility=facility).count()
            occupied = ParkingSpot.objects.filter(
                facility=facility, is_available=False).count()
            revenue = sum(
                spot.price_per_hour for spot in ParkingSpot.objects.filter(facility=facility))
            occupancy_rate = (occupied / total_spots) * \
                100 if total_spots > 0 else 0

            facility_metrics.append({
                "facility_name": facility.name,
                "total_spots": total_spots,
                "occupied_spots": occupied,
                "revenue": revenue,
                "occupancy_rate": occupancy_rate,
            })

        return Response({
            "managed_facilities_count": facilities.count(),
            "active_spots": active_spots,
            "past_bookings": past_bookings.count(),
            "occupied_spots": occupied_spots,
            'total_spending' : total_spending,
            "recent_bookings": list(recent_bookings.values('id', 'user__email', 'parking_spot__facility__name', 'start_time')),
            "upcoming_bookings": upcoming_bookings.values('parking_spot__facility__name', 'start_time', 'end_time'),
            "facility_metrics": facility_metrics,
            "recent_activity": recent_activity.values('id', 'user__email', 'parking_spot__facility__name', 'start_time')
        })


class ProviderDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsProviderOrAdmin]

    def get(self, request):
        facilities = ParkingFacility.objects.filter(provider=request.user)
        spots = ParkingSpot.objects.filter(facility__in=facilities)
        bookings = Booking.objects.filter(parking_spot__in=spots)

        daily_bookings = (
            bookings.annotate(day=TruncDay("start_time"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        total_spots = spots.count()
        total_bookings = bookings.count()
        avg_price = spots.aggregate(avg=Avg("price_per_hour"))["avg"] or 0

        occupied_spots = spots.filter(is_available=False).count()

        # Recent activity (recent bookings)
        recent_activity = bookings.order_by('-start_time')[:5].values(
            'id', 'user__email', 'parking_spot__facility__name', 'start_time'
        )

        return Response({
            "facilities_count": facilities.count(),
            "spots_count": total_spots,
            "total_bookings": total_bookings,
            "avg_price": avg_price,
            "occupied_spots": occupied_spots,
            "booking_trends": daily_bookings,
            "facility_metrics": self.get_facility_metrics(facilities),
            "recent_activity": list(recent_activity),
        })

    def get_facility_metrics(self, facilities):
        metrics = []
        for facility in facilities:
            spots = ParkingSpot.objects.filter(facility=facility)
            occupied_spots = spots.filter(is_available=False).count()
            total_revenue = sum(
                [spot.price_per_hour for spot in spots if spot.is_available == False])
            occupancy_rate = (occupied_spots / len(spots)) * \
                100 if len(spots) > 0 else 0
            metrics.append({
                "facility_name": facility.name,
                "total_spots": len(spots),
                "occupied_spots": occupied_spots,
                "total_revenue": total_revenue,
                "occupancy_rate": occupancy_rate
            })
        return metrics


class SpotEvaluationReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role not in ["provider", "admin"] and not user.is_staff:
            return Response({"error": "Not authorized"}, status=403)

        spots = ParkingSpot.objects.all()
        if user.role == "provider":
            spots = spots.filter(provider=user)

        report = []
        for spot in spots:
            preds = SpotPredictionLog.objects.filter(parking_spot=spot)
            logs = SpotAvailabilityLog.objects.filter(parking_spot=spot)

            if not preds.exists() or not logs.exists():
                continue

            df_preds = pd.DataFrame(
                list(preds.values("predicted_for_time", "probability")))
            df_logs = pd.DataFrame(
                list(logs.values("timestamp", "is_available")))

            df = pd.merge_asof(
                df_preds.sort_values("predicted_for_time"),
                df_logs.sort_values("timestamp"),
                left_on="predicted_for_time",
                right_on="timestamp",
                direction="nearest"
            )

            if df.empty:
                continue

            y_true = df["is_available"].astype(int)
            y_pred = (df["probability"] > 0.5).astype(int)

            report.append({
                "spot": spot.name,
                "precision": precision_score(y_true, y_pred, zero_division=0),
                "recall": recall_score(y_true, y_pred, zero_division=0),
                "f1": f1_score(y_true, y_pred, zero_division=0),
            })

        return Response(report)
