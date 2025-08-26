import django.utils
import math
from geopy.distance import geodesic
import requests
from rest_framework import generics, permissions, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from math import radians
from django.utils import timezone
from accounts.utils import IsProviderOrAdmin, IsAdminOrSuperuser, IsAdminOrFacilityProvider, log_action
from notifications.models import Notification
from notifications.tasks import send_notification_async
from parking.utils import calculate_distance
from .models import ArchiveReport, ParkingFacility, ParkingSpot, Booking, SpotAvailabilityLog, SpotPredictionLog, SpotPriceLog
from .serializers import (
    ArchiveReportSerializer, ParkingFacilitySerializer, ParkingSpotSerializer, BookingSerializer,
    SpotReviewSerializer, SpotAvailabilityLogSerializer, SpotPredictionSerializer, SpotPriceLogSerializer
)
from .prediction_service import predict_spots_nearby
from core.metrics import (
    PREDICTION_REQUESTS, PREDICTION_LATENCY, PREDICTION_SAVED,
    BOOKING_CREATED, BOOKING_ENDED, ACTIVE_AVAILABLE_SPOTS, SPOT_SELECTED
)
from .pricing import update_dynamic_prices

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def update_available_spots_metric():
    ACTIVE_AVAILABLE_SPOTS.set(
        ParkingSpot.objects.filter(is_available=True).count())
    log_action(None, "update_available_spots_metric",
               f"Updated available spots metric: {ACTIVE_AVAILABLE_SPOTS._value.get()}", None)


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def trigger_dynamic_pricing(request):
    updated = update_dynamic_prices(user=request.user)
    return Response({"updated": updated})


class ParkingFacilityView(viewsets.ModelViewSet):
    serializer_class = ParkingFacilitySerializer
    permission_classes = [IsProviderOrAdmin, IsAdminOrFacilityProvider]

    def get_queryset(self):
        user = self.request.user
        qs = ParkingFacility.objects.all()
        include_archived = self.request.query_params.get("include_archived")
        only_archived = self.request.query_params.get("only_archived")
        if not (user.role == 'provider' or user.is_staff):
            log_action(user, "view_facilities_denied",
                       "User attempted to view facilities without permission", user.ip_address)
            raise PermissionDenied(
                "Only providers or admins can view facilities.")

        if only_archived:
            qs = qs.filter(is_active=False)
        elif not include_archived:
            qs = qs.filter(is_active=True)

        if user.role == 'provider':
            qs = qs.filter(provider=user)
            log_action(user, "view_facilities",
                       f"User viewed facilities for provider {user.username}", user.ip_address)
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'provider' and not self.request.user.is_staff:
            log_action(self.request.user, "create_facility_denied",
                       "User attempted to create a facility without permission", self.request.ip_address)
            raise PermissionDenied(
                "Only providers or admins can create facilities.")
        serializer.save(provider=self.request.user)
        log_action(self.request.user, "create_facility",
                   "User created a new parking facility", self.request)
        update_available_spots_metric()

    def perform_destroy(self, instance):
        instance.soft_delete()
        log_action(self.request.user, "delete_facility",
                   f"User deleted facility {instance.name}", self.request)
        update_available_spots_metric()

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        facility = self.get_object()
        facility.is_archived = True
        facility.save()
        log_action(request.user, "archive_facility",
                   f"Archived facility {facility.name}", request)
        return Response({"status": "archived"})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        facility = ParkingFacility.all_objects.get(pk=pk)
        facility.is_archived = False
        facility.save()
        log_action(request.user, "restore_facility",
                   f"Restored facility {facility.name}", request)
        return Response({"status": "restored"})

    @action(detail=False, methods=["post"])
    def bulk_archive(self, request):
        ids = request.data.get("ids", [])
        updated = ParkingFacility.objects.filter(
            id__in=ids).update(is_active=False)
        log_action(request.user, "bulk_archive_facilities",
                   f"Archived {updated} facilities", request)
        return Response({"archived": updated}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def bulk_restore(self, request):
        ids = request.data.get("ids", [])
        updated = ParkingFacility.objects.filter(
            id__in=ids).update(is_active=True)
        log_action(request.user, "bulk_restore_facilities",
                   f"Restored {updated} facilities", request)
        return Response({"restored": updated}, status=status.HTTP_200_OK)


class ParkingSpotViewSet(viewsets.ModelViewSet):
    serializer_class = ParkingSpotSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsProviderOrAdmin]

    def get_queryset(self):
        qs = ParkingSpot.objects.all()

        include_archived = self.request.query_params.get("include_archived")
        only_archived = self.request.query_params.get("only_archived")

        if only_archived:
            qs = qs.filter(is_active=False)
        elif not include_archived:
            qs = qs.filter(is_active=True)

        user = self.request.user
        if user.role == 'provider':
            qs = qs.filter(provider=user)

        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'provider' and not self.request.user.is_staff:
            log_action(self.request.user, "create_spot_denied",
                       "User attempted to create a parking spot without permission", self.request.ip_address)
            raise PermissionDenied("Only providers or admins can add spots.")
        spot = serializer.save(provider=self.request.user)
        SpotAvailabilityLog.objects.create(
            parking_spot=spot, is_available=spot.is_available)
        log_action(self.request.user, "create_spot",
                   f"User created parking spot {spot.name}", self.request)
        update_available_spots_metric()

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        spot = ParkingSpot.objects.get(pk=pk)
        spot.is_archived = True
        spot.save()
        log_action(request.user, "archive_spot",
                   f"Archived spot {spot.name}", request)
        return Response({"status": "archived"})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        spot = ParkingSpot.all_objects.get(pk=pk)
        spot.is_archived = False
        spot.save()
        log_action(request.user, "restore_spot",
                   f"Restored spot {spot.name}", request)
        return Response({"status": "restored"})

    def perform_destroy(self, instance):
        instance.soft_delete()
        log_action(self.request.user, "soft_delete_spot",
                   f"Archived spot {instance.name}", self.request)

    @action(detail=False, methods=["post"])
    def bulk_archive(self, request):
        ids = request.data.get("ids", [])
        updated = ParkingSpot.objects.filter(
            id__in=ids).update(is_active=False)
        log_action(request.user, "bulk_archive_spots",
                   f"Archived {updated} spots", request)
        return Response({"archived": updated}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def bulk_restore(self, request):
        ids = request.data.get("ids", [])
        updated = ParkingSpot.objects.filter(id__in=ids).update(is_active=True)
        log_action(request.user, "bulk_restore_spots",
                   f"Restored {updated} spots", request)
        return Response({"restored": updated}, status=status.HTTP_200_OK)


class NearbyParkingSpotsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius_km = float(request.query_params.get("radius", 200))

        if not lat or not lng:
            return Response({"error": "Latitude and longitude are required."}, status=400)

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response({"error": "Invalid coordinates."}, status=400)

        # Step 1: check DB spots using geopy
        spots = ParkingSpot.objects.filter(is_available=True)
        nearby_spots = [
            spot for spot in spots
            if geodesic(
                (lat, lng),
                (float(spot.latitude), float(spot.longitude))
            ).km <= radius_km
        ]

        if nearby_spots:
            serializer = ParkingSpotSerializer(nearby_spots, many=True)
            self._notify_user(request, len(nearby_spots),
                              radius_km, source="database")
            return Response({
                "source": "database",
                "results": serializer.data,
                "within_radius": len(nearby_spots),
                "radius": radius_km
            })

        # Step 2: query Overpass API
        results = self.query_overpass(lat, lng, radius_km)

        if results:
            cached_spots = self.cache_osm_spots(results)
            serializer = ParkingSpotSerializer(cached_spots, many=True)
            self._notify_user(request, len(cached_spots),
                              radius_km, source="osm")
            return Response({
                "source": "osm",
                "results": serializer.data,
                "within_radius": len(cached_spots),
                "radius": radius_km
            })

        # Step 3: Expand search up to 200km (cap at 500km)
        if radius_km < 200:
            new_radius = min(radius_km * 10, 500)
            return self._retry_with_expanded_radius(request, lat, lng, new_radius)

        # Step 4: No results
        self._notify_user(request, 0, radius_km, source="none")
        return Response({
            "message": f"No parking found within {radius_km} km.",
            "results": []
        }, status=200)

    # Helper methods
    def query_overpass(self, lat, lng, radius_km):
        radius_m = int(radius_km * 1000)
        query = f"""
        [out:json];
        (
          node["amenity"="parking"](around:{radius_m},{lat},{lng});
          way["amenity"="parking"](around:{radius_m},{lat},{lng});
          relation["amenity"="parking"](around:{radius_m},{lat},{lng});
        );
        out center;
        """
        url = "https://overpass-api.de/api/interpreter"
        resp = requests.post(url, data={"data": query}, timeout=25)
        data = resp.json()

        results = []
        for el in data.get("elements", []):
            results.append({
                "id": el.get("id"),
                "name": el.get("tags", {}).get("name", "Unnamed Parking"),
                "lat": el.get("lat") or el.get("center", {}).get("lat"),
                "lng": el.get("lon") or el.get("center", {}).get("lon"),
                "tags": el.get("tags", {}),
            })
        return results

    def cache_osm_spots(self, results):
        """Save OSM results into DB if not already stored"""
        cached = []
        for r in results:
            spot, _ = ParkingSpot.objects.get_or_create(
                external_id=str(r["id"]),
                defaults={
                    "name": r["name"],
                    "latitude": r["lat"],
                    "longitude": r["lng"],
                    "is_available": True,
                    "source": "osm",  # mark source if you have this field
                },
            )
            cached.append(spot)
        return cached

    def _retry_with_expanded_radius(self, request, lat, lng, new_radius):
        """Retry search with expanded radius"""
        request.GET._mutable = True
        request.GET["radius"] = str(new_radius)
        return self.get(request)

    def _notify_user(self, request, count, radius_km, source="database"):
        """Send notification to user or fallback to public"""
        if count > 0:
            title = "Nearby Parking Found 🚗"
            body = f"{count} parking spots found within {radius_km} km ({source})."
        else:
            title = "No Parking Nearby ❌"
            body = f"No parking spots found within {radius_km} km."

        if request.user.is_authenticated:
            send_notification_async.delay(request.user.id, title, body)
        else:
            Notification.objects.create(
                user=None,
                title=title,
                body=body,
                type="public",
                status="pending",
                delivered=False,
                sent_at=timezone.now(),
            )


class NearbyPredictionsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        PREDICTION_REQUESTS.inc()
        with PREDICTION_LATENCY.time():
            lat = request.query_params.get('lat')
            lng = request.query_params.get('lng')
            radius_km = float(request.query_params.get(
                'radius', getattr(request.user, 'default_radius_km', 2)))
            time_ahead = int(request.query_params.get('time_ahead', 15))

            if not lat or not lng:
                log_action(request.user, "nearby_spots_error",
                           "Latitude and longitude not provided", request)
                return Response({"error": "lat and lng are required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                lat = float(lat)
                lng = float(lng)
            except ValueError:
                log_action(request.user, "nearby_spots_error",
                           "Invalid coordinates", request)
                return Response({"error": "invalid coordinates"}, status=status.HTTP_400_BAD_REQUEST)

            lat_delta = radius_km / 111.0
            lng_delta = radius_km / \
                (111.0 * abs(math.cos(radians(lat))) or 1.0)

            candidates = ParkingSpot.objects.filter(
                latitude__gte=lat - lat_delta,
                latitude__lte=lat + lat_delta,
                longitude__gte=lng - lng_delta,
                longitude__lte=lng + lng_delta,
            )

            candidate_list = []
            for s in candidates:
                dist = calculate_distance(
                    lat, lng, float(s.latitude), float(s.longitude))
                if dist <= radius_km:
                    candidate_list.append(s)

            predictions = predict_spots_nearby(
                candidate_list, time_ahead_minutes=time_ahead)

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
            log_action(request.user, "view_nearby_spots",
                       f"User viewed nearby spots within {radius_km} km", request)
            update_available_spots_metric()
            return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        spot_id = request.data.get("parking_spot")
        try:
            spot = ParkingSpot.objects.get(id=spot_id, is_available=True)
            send_notification_async(
                spot.user,
                "booking_created",
                {"spot_name": spot.name, "facility_name": spot.facility.name},
            )
            log_action(request.user, "book_parking_spot",
                       f"User attempted to book parking spot {spot.name}", request)
        except ParkingSpot.DoesNotExist:
            log_action(request.user, "book_parking_spot_error",
                       "User attempted to book a non-existent or unavailable parking spot", request)
            return Response({"error": "Spot not available"}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.create(user=request.user, parking_spot=spot)
        spot.is_available = False
        spot.save()
        update_available_spots_metric()
        log_action(request.user, "book_parking_spot",
                   f"User booked parking spot {spot.name}", request)
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def end_booking(self, request, pk=None):
        try:
            booking = Booking.objects.get(
                pk=pk, user=request.user, is_active=True)
            log_action(request.user, "end_booking",
                       f"User ended booking for spot {booking.parking_spot.name}", request)
        except Booking.DoesNotExist:
            log_action(request.user, "end_booking_error",
                       "User attempted to end a non-existent or already ended booking", request)
            return Response({"error": "Booking not found or already ended"}, status=404)

        booking.end_booking()
        BOOKING_ENDED.inc()
        update_available_spots_metric()
        log_action(request.user, "booking_ended",
                   f"User ended booking for spot {booking.parking_spot.name}", request)
        return Response({"message": "Booking ended, spot is now free"})


class NavigateToSpotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, spot_id):
        try:
            spot = ParkingSpot.objects.get(id=spot_id)
            log_action(request.user, "navigate_to_spot",
                       f"User requested navigation to spot {spot.name}", request)
        except ParkingSpot.DoesNotExist:
            log_action(request.user, "navigate_to_spot_error",
                       "User attempted to navigate to a non-existent parking spot", request)
            return Response({"error": "Spot not found"}, status=404)

        send_notification_async.delay(
            request.user.id,
            "📍 Starting Navigation",
            f"Navigate to {spot.name}. Drive safely!",
            type_="navigation_start",
            extra={"spot_id": spot.id, "latitude": spot.latitude,
                   "longitude": spot.longitude}
        )

        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={spot.latitude},{spot.longitude}"
        SPOT_SELECTED.inc()
        update_available_spots_metric()
        log_action(request.user, "navigate_to_spot",
                   f"User navigated to spot {spot.name}", request)
        return Response({"navigation_url": maps_url})


class SpotReviewCreateView(generics.CreateAPIView):
    serializer_class = SpotReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        log_action(self.request.user, "spot_review_created",
                   "User created a spot review", self.request)


class SpotAvailabilityLogListView(generics.ListAPIView):
    queryset = SpotAvailabilityLog.objects.all()
    serializer_class = SpotAvailabilityLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        if user.role == "provider":
            return SpotAvailabilityLog.objects.filter(
                parking_spot__facility__provider=user).order_by("-created_at")
        elif user.is_staff:
            return SpotAvailabilityLog.objects.all().order_by("-created_at")
        return SpotAvailabilityLog.objects.none()


class SpotPriceLogView(generics.ListAPIView):
    serializer_class = SpotPriceLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "provider":
            return SpotPriceLog.objects.filter(parking_spot__facility__provider=user).order_by("-updated_at")
        elif user.is_staff:
            return SpotPriceLog.objects.all().order_by("-updated_at")
        return SpotPriceLog.objects.none()


class ArchiveReportListView(generics.ListAPIView):
    serializer_class = ArchiveReportSerializer
    permission_classes = [IsAdminOrSuperuser]

    def get_queryset(self):
        return ArchiveReport.objects.all().order_by("-created_at")
