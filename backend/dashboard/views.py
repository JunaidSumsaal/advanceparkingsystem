from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from accounts.utils import IsAttendant, IsDriver, IsProviderOrAdmin
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


class DriverDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsDriver]

    def get(self, request):
        active_bookings = Booking.objects.filter(user=request.user, is_active=True).count()
        past_bookings = Booking.objects.filter(user=request.user, is_active=False).count()
        return Response({
            "active_bookings": active_bookings,
            "past_bookings": past_bookings,
        })

class AttendantDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAttendant]

    def get(self, request):
        facilities = ParkingFacility.objects.filter(attendants=request.user)
        active_spots = ParkingSpot.objects.filter(facility__in=facilities, is_available=True).count()
        occupied_spots = ParkingSpot.objects.filter(facility__in=facilities, is_available=False).count()
        return Response({
            "managed_facilities": facilities.count(),
            "active_spots": active_spots,
            "occupied_spots": occupied_spots,
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
        return Response({
            "facilities_count": facilities.count(),
            "spots_count": spots.count(),
            "total_bookings": bookings.count(),
            "avg_price": spots.aggregate(avg=Avg("price_per_hour"))["avg"] or 0,
        })


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

            df_preds = pd.DataFrame(list(preds.values("predicted_for_time", "probability")))
            df_logs = pd.DataFrame(list(logs.values("timestamp", "is_available")))

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
