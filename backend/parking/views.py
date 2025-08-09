from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from math import radians, sin, cos, sqrt, atan2
from .models import ParkingSpot, Booking, SpotAvailabilityLog
from .serializers import (
    ParkingSpotSerializer, BookingSerializer,
    SpotReviewSerializer, SpotAvailabilityLogSerializer
)

# Distance calculation
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

class ParkingSpotListCreateView(generics.ListCreateAPIView):
    queryset = ParkingSpot.objects.all()
    serializer_class = ParkingSpotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.role != 'provider' and not self.request.user.is_staff:
            return Response({"error": "Only providers or admins can add spots."}, status=403)
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

class BookParkingSpotView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
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

    def end_booking(self, request, pk=None):
        try:
            booking = Booking.objects.get(pk=pk, user=request.user, is_active=True)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found or already ended"}, status=404)

        booking.end_booking()
        return Response({"message": "Booking ended, spot is now free"})

class NavigateToSpotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, spot_id):
        try:
            spot = ParkingSpot.objects.get(id=spot_id)
        except ParkingSpot.DoesNotExist:
            return Response({"error": "Spot not found"}, status=404)
        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={spot.latitude},{spot.longitude}"
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

class ParkingSpotPollingView(APIView):
    def get(self, request):
        spots = ParkingSpot.objects.all()
        serializer = ParkingSpotSerializer(spots, many=True)
        return Response(serializer.data)
