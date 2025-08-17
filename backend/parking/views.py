import math
from rest_framework import generics, permissions, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from math import radians
from accounts.utils import IsProviderOrAdmin, IsAdminOrSuperuser, IsAttendantOrDriver, IsAdminOrFacilityProvider, log_action
from parking.utils import calculate_distance
from .models import ParkingFacility, ParkingSpot, Booking, SpotAvailabilityLog, SpotPredictionLog
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
    log_action(None, "update_available_spots_metric", f"Updated available spots metric: {ACTIVE_AVAILABLE_SPOTS._value.get()}", None)

class ParkingFacilityView(viewsets.ModelViewSet):
    serializer_class = ParkingFacilitySerializer
    permission_classes = [IsProviderOrAdmin, IsAdminOrFacilityProvider]

    def get_queryset(self):
        user = self.request.user
        qs = ParkingFacility.objects.all()
        if not (user.role == 'provider' or user.is_staff):
            log_action(user, "view_facilities_denied", "User attempted to view facilities without permission", user.ip_address)
            raise PermissionDenied("Only providers or admins can view facilities.")
        if user.role == 'provider':
            qs = qs.filter(provider=user)
            log_action(user, "view_facilities", f"User viewed facilities for provider {user.username}", user.ip_address)
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'provider' and not self.request.user.is_staff:
            log_action(self.request.user, "create_facility_denied", "User attempted to create a facility without permission", self.request.ip_address)
            raise PermissionDenied("Only providers or admins can create facilities.")
        serializer.save(provider=self.request.user)
        log_action(self.request.user, "create_facility", "User created a new parking facility", self.request)
        update_available_spots_metric()

    def perform_destroy(self, instance):
        instance.delete()
        log_action(self.request.user, "delete_facility", f"User deleted facility {instance.name}", self.request)
        update_available_spots_metric()

class ParkingSpotListCreateView(generics.ListCreateAPIView):
    queryset = ParkingSpot.objects.all()
    serializer_class = ParkingSpotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsProviderOrAdmin]

    def perform_create(self, serializer):
        if self.request.user.role != 'provider' and not self.request.user.is_staff:
            log_action(self.request.user, "create_spot_denied", "User attempted to create a parking spot without permission", self.request.ip_address)
            raise PermissionDenied("Only providers or admins can add spots.")
        spot = serializer.save(provider=self.request.user)
        SpotAvailabilityLog.objects.create(parking_spot=spot, is_available=spot.is_available)
        log_action(self.request.user, "create_spot", f"User created parking spot {spot.name}", self.request)
        update_available_spots_metric()

class NearbyParkingSpotsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius_km = float(request.query_params.get('radius', getattr(request.user, 'default_radius_km', 2)))

        if not lat or not lng:
            log_action(request.user, "nearby_spots_error", "Latitude and longitude not provided", request)
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
        log_action(request.user, "nearby_spots_viewed", f"User viewed nearby spots within {radius_km} km", request)
        update_available_spots_metric()
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
                log_action(request.user, "nearby_spots_error", "Latitude and longitude not provided", request)
                return Response({"error": "lat and lng are required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                lat = float(lat)
                lng = float(lng)
            except ValueError:
                log_action(request.user, "nearby_spots_error", "Invalid coordinates", request)
                return Response({"error": "invalid coordinates"}, status=status.HTTP_400_BAD_REQUEST)

            lat_delta = radius_km / 111.0
            lng_delta = radius_km / (111.0 * abs(math.cos(radians(lat))) or 1.0)

            candidates = ParkingSpot.objects.filter(
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
                prob = float(p['probability'])
                pred_time = p['predicted_for_time']

                SpotPredictionLog.objects.create(
                    parking_spot=spot,
                    probability=prob,
                    predicted_for_time=pred_time,
                    model_version="v1"
                )

                response_data.append({
                    "id": spot.id,
                    "name": spot.name,
                    "latitude": spot.latitude,
                    "longitude": spot.longitude,
                    "probability": round(prob, 3),
                    "predicted_for_time": pred_time
                })

            serializer = SpotPredictionSerializer(response_data, many=True)
            PREDICTION_SAVED.inc(len(response_data))
            log_action(request.user, "view_nearby_spots", f"User viewed nearby spots within {radius_km} km", request)
            update_available_spots_metric()
            return Response(serializer.data)


class BookParkingSpotView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        BOOKING_CREATED.inc()
        spot = serializer.validated_data['parking_spot']
        if spot.provider == self.request.user:
            log_action(self.request.user, "booking_own_spot_denied", "User attempted to book their own parking spot", self.request)
            raise PermissionDenied("You cannot book your own spot.")
        if not spot.is_available:
            log_action(self.request.user, "booking_spot_unavailable", "User attempted to book an unavailable parking spot", self.request)
            raise PermissionDenied("Spot is not available.")
        serializer.save(user=self.request.user)
        update_available_spots_metric()
        log_action(self.request.user, "book_parking_spot", f"User booked parking spot {spot.name}", self.request)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        spot_id = request.data.get("parking_spot")
        try:
            spot = ParkingSpot.objects.get(id=spot_id, is_available=True)
            log_action(request.user, "book_parking_spot", f"User attempted to book parking spot {spot.name}", request)
        except ParkingSpot.DoesNotExist:
            log_action(request.user, "book_parking_spot_error", "User attempted to book a non-existent or unavailable parking spot", request)
            return Response({"error": "Spot not available"}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.create(user=request.user, parking_spot=spot)
        spot.is_available = False
        spot.save()
        update_available_spots_metric()
        log_action(request.user, "book_parking_spot", f"User booked parking spot {spot.name}", request)
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def end_booking(self, request, pk=None):
        try:
            booking = Booking.objects.get(pk=pk, user=request.user, is_active=True)
            log_action(request.user, "end_booking", f"User ended booking for spot {booking.parking_spot.name}", request)
        except Booking.DoesNotExist:
            log_action(request.user, "end_booking_error", "User attempted to end a non-existent or already ended booking", request)
            return Response({"error": "Booking not found or already ended"}, status=404)

        booking.end_booking()
        BOOKING_ENDED.inc()
        update_available_spots_metric()
        log_action(request.user, "booking_ended", f"User ended booking for spot {booking.parking_spot.name}", request)
        return Response({"message": "Booking ended, spot is now free"})

class NavigateToSpotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, spot_id):
        try:
            spot = ParkingSpot.objects.get(id=spot_id)
            log_action(request.user, "navigate_to_spot", f"User requested navigation to spot {spot.name}", request)
        except ParkingSpot.DoesNotExist:
            log_action(request.user, "navigate_to_spot_error", "User attempted to navigate to a non-existent parking spot", request)
            return Response({"error": "Spot not found"}, status=404)
        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={spot.latitude},{spot.longitude}"
        SPOT_SELECTED.inc()
        update_available_spots_metric()
        log_action(request.user, "navigate_to_spot", f"User navigated to spot {spot.name}", request)
        return Response({"navigation_url": maps_url})

class SpotReviewCreateView(generics.CreateAPIView):
    serializer_class = SpotReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        log_action(self.request.user, "spot_review_created", "User created a spot review", self.request)

class SpotAvailabilityLogListView(generics.ListAPIView):
    queryset = SpotAvailabilityLog.objects.all()
    serializer_class = SpotAvailabilityLogSerializer
    permission_classes = [permissions.IsAdminUser]
