import math
from rest_framework import generics, permissions, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from math import radians
from accounts.utils import IsProviderOrAdmin, IsAdminOrSuperuser, IsAttendantOrDriver, IsAdminOrFacilityProvider
from parking.utils import calculate_distance
from .models import ParkingFacility, ParkingSpot, Booking, SpotAvailabilityLog
from .serializers import (
    ParkingFacilitySerializer, ParkingSpotSerializer, BookingSerializer,
    SpotReviewSerializer, SpotAvailabilityLogSerializer, SpotPredictionSerializer
)
from .prediction_service import predict_spots_nearby
from core.metrics import (
    PREDICTION_REQUESTS, PREDICTION_LATENCY, PREDICTION_SAVED,
    BOOKING_CREATED, BOOKING_ENDED, ACTIVE_AVAILABLE_SPOTS, SPOT_SELECTED
)

def update_available_spots_metric():
    ACTIVE_AVAILABLE_SPOTS.set(ParkingSpot.objects.filter(is_available=True).count())

class ParkingFacilityView(viewsets.ModelViewSet):
    serializer_class = ParkingFacilitySerializer
    permission_classes = [IsProviderOrAdmin, IsAdminOrFacilityProvider]

    def get_queryset(self):
        user = self.request.user
        qs = ParkingFacility.objects.all()
        if not (user.role == 'provider' or user.is_staff):
            raise PermissionDenied("Only providers or admins can view facilities.")
        if user.role == 'provider':
            qs = qs.filter(provider=user)
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'provider' and not self.request.user.is_staff:
            raise PermissionDenied("Only providers or admins can create facilities.")
        serializer.save(provider=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

class ParkingSpotListCreateView(generics.ListCreateAPIView):
    queryset = ParkingSpot.objects.all()
    serializer_class = ParkingSpotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsProviderOrAdmin]

    def perform_create(self, serializer):
        if self.request.user.role != 'provider' and not self.request.user.is_staff:
            raise PermissionDenied("Only providers or admins can add spots.")
        spot = serializer.save(provider=self.request.user)
        SpotAvailabilityLog.objects.create(parking_spot=spot, is_available=spot.is_available)

class NearbyParkingSpotsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius_km = float(request.query_params.get('radius', getattr(request.user, 'default_radius_km', 2)))

        if not lat or not lng:
            return Response({"error": "Latitude and longitude are required."}, status=400)

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response({"error": "Invalid coordinates."}, status=400)

        spots = ParkingSpot.objects.filter(is_available=True)
        nearby_spots = [
            spot for spot in spots
            if calculate_distance(lat, lng, float(spot.latitude), float(spot.longitude)) <= radius_km
        ]
        serializer = ParkingSpotSerializer(nearby_spots, many=True)
        return Response(serializer.data)

class NearbyPredictionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        PREDICTION_REQUESTS.inc()
        with PREDICTION_LATENCY.time():
            lat = request.query_params.get('lat')
            lng = request.query_params.get('lng')
            radius_km = float(request.query_params.get('radius', getattr(request.user, 'default_radius_km', 2)))
            time_ahead = int(request.query_params.get('time_ahead', 15))
            if not lat or not lng:
                return Response({"error": "lat and lng are required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                lat = float(lat)
                lng = float(lng)
            except ValueError:
                return Response({"error": "invalid coordinates"}, status=status.HTTP_400_BAD_REQUEST)
            lat_delta = radius_km / 111.0
            lng_delta = radius_km / (111.0 * abs(math.cos(radians(lat))) or 1.0)
            candidates = ParkingSpot.objects.filter(
                is_available=True,
                latitude__gte=lat - lat_delta,
                latitude__lte=lat + lat_delta,
                longitude__gte=lng - lng_delta,
                longitude__lte=lng + lng_delta,
            )
            candidate_list = []
            for s in candidates:
                dist = calculate_distance(lat, lng, float(s.latitude), float(s.longitude))
                if dist <= radius_km:
                    candidate_list.append(s)
            predictions = predict_spots_nearby(candidate_list, time_ahead_minutes=time_ahead)
            response_data = []
            for p in predictions:
                spot = p['spot']
                response_data.append({
                    "id": spot.id,
                    "name": spot.name,
                    "latitude": spot.latitude,
                    "longitude": spot.longitude,
                    "probability": round(p['probability'], 3),
                    "predicted_for_time": p['predicted_for_time']
                })
            serializer = SpotPredictionSerializer(response_data, many=True)
            PREDICTION_SAVED.inc(len(response_data))
            return Response(serializer.data)

class BookParkingSpotView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        BOOKING_CREATED.inc()
        spot = serializer.validated_data['parking_spot']
        if spot.provider == self.request.user:
            raise PermissionDenied("You cannot book your own spot.")
        if not spot.is_available:
            raise PermissionDenied("Spot is not available.")
        serializer.save(user=self.request.user)
        update_available_spots_metric()

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        spot_id = request.data.get("parking_spot")
        try:
            spot = ParkingSpot.objects.get(id=spot_id, is_available=True)
        except ParkingSpot.DoesNotExist:
            return Response({"error": "Spot not available"}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.create(user=request.user, parking_spot=spot)
        spot.is_available = False
        spot.save()
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def end_booking(self, request, pk=None):
        try:
            booking = Booking.objects.get(pk=pk, user=request.user, is_active=True)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found or already ended"}, status=404)

        booking.end_booking()
        BOOKING_ENDED.inc()
        update_available_spots_metric()
        return Response({"message": "Booking ended, spot is now free"})

class NavigateToSpotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, spot_id):
        try:
            spot = ParkingSpot.objects.get(id=spot_id)
        except ParkingSpot.DoesNotExist:
            return Response({"error": "Spot not found"}, status=404)
        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={spot.latitude},{spot.longitude}"
        SPOT_SELECTED.inc()
        return Response({"navigation_url": maps_url})

class SpotReviewCreateView(generics.CreateAPIView):
    serializer_class = SpotReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SpotAvailabilityLogListView(generics.ListAPIView):
    queryset = SpotAvailabilityLog.objects.all()
    serializer_class = SpotAvailabilityLogSerializer
    permission_classes = [permissions.IsAdminUser]
