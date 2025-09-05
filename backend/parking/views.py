import logging
import math
import requests
from math import radians
from typing import List, Dict, Tuple, Set
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from parking.utils import calculate_distance
from rest_framework import generics, permissions, viewsets, status
from geopy.distance import geodesic
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from accounts.utils import IsProviderOrAdmin, IsAdminOrSuperuser, IsAdminOrFacilityProvider, log_action
from notifications.models import Notification
from notifications.tasks import send_notification_async
from .models import ArchiveReport, ParkingFacility, ParkingSpot, Booking, SpotAvailabilityLog, SpotPredictionLog, SpotPriceLog
from .serializers import (
    ArchiveReportSerializer, ParkingFacilitySerializer, ParkingSpotSerializer, BookingSerializer,
    SpotReviewSerializer, SpotAvailabilityLogSerializer, SpotPredictionSerializer, SpotPriceLogSerializer
)
from .prediction_service import predict_spots_nearby
from geopy.distance import distance as geopy_distance
from .utils import (
    query_overpass_any,
    send_websocket_update,
)
from core.metrics import (
    PREDICTION_REQUESTS, PREDICTION_LATENCY, PREDICTION_SAVED,
    BOOKING_ENDED, ACTIVE_AVAILABLE_SPOTS, SPOT_SELECTED
)
from .pricing import update_dynamic_prices

logger = logging.getLogger(__name__)
User = get_user_model()


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
        try:
            # -------------------------
            # Parse & validate params
            # -------------------------
            lat, lng, radius_km, limit = self._parse_params(request)
            if isinstance(lat, Response):  # validation failed
                logger.warning("Invalid input params: %s",
                               request.query_params)
                return lat

            target_count = settings.PARKING.get("TARGET_RESULT_COUNT", 60)

            # -------------------------
            # 1. DB lookup
            # -------------------------
            spots = self._get_from_db(lat, lng, radius_km, limit)
            if spots:
                logger.info("DB spots found: %d", len(spots))
                self._notify_user(request, len(spots),
                                  radius_km, source="database")
                return self._build_response(request, spots, radius_km, "db", limit)

            # -------------------------
            # 2. Cache lookup
            # -------------------------
            cache_key = f"osm:{lat:.2f}:{lng:.2f}:{radius_km:.0f}"
            cached = cache.get(cache_key)
            if cached:
                logger.info("Cache spots found: %d (cache_key=%s)",
                            len(cached), cache_key)
                self._notify_user(request, len(cached),
                                  radius_km, source="cache")
                return self._build_response(request, cached, radius_km, "cache", limit)

            # -------------------------
            # 3. Expansion strategy
            # -------------------------
            collected, sources_used = self._expand_with_osm(
                lat, lng, radius_km, target_count)
            if collected:
                logger.info("Expanded OSM query success: %d spots",
                            len(collected))
                self._cache_osm_spots(collected)  # Cache the newly found spots
                # Save IDs to main cache key
                self._save_to_cache(cache_key, collected)
                self._broadcast_ws(collected)  # Broadcast to websockets
                self._notify_user(request, len(collected),
                                  radius_km, source=",".join(sources_used))
                return self._build_response(request, collected, radius_km, ",".join(sources_used), limit)

            # -------------------------
            # 4. Graceful fallback
            # -------------------------
            logger.warning("No parking found after all strategies")
            self._notify_user(request, 0, radius_km, source="none")
            return Response({"message": "No parking found", "source": "none", "results": [], "within_radius": 0, "radius": radius_km}, status=404)

        except Exception as e:
            logger.error("NearbyParkingSpotsView error: %s",
                         str(e), exc_info=True)
            return Response({"error": "Internal server error"}, status=500)

    # -------------------------
    # DB lookup
    # -------------------------
    def _get_from_db(self, lat, lng, radius_km, limit):
        qs = ParkingSpot.objects.filter(is_active=True, is_archived=False)
        nearby = []
        for spot in qs:
            try:
                dist = geopy_distance(
                    (lat, lng), (spot.latitude, spot.longitude)).km
                if dist <= radius_km:
                    nearby.append(spot)
            except Exception as e:
                logger.warning(
                    "Distance calc failed for spot %s: %s", spot.id, str(e))
        return nearby[:limit] if nearby else None

    # -------------------------
    # Expansion with OSM
    # -------------------------
    def _expand_with_osm(self, lat, lng, radius_km, target_count):
        collected = []
        sources_used = []
        expansion_radii = settings.PARKING.get(
            "EXPANSION_RADII_KM", [5, 10, 20, 30, 50, 100, 150, 200])

        for r in expansion_radii:
            if r > radius_km:
                continue
            osm = query_overpass_any(lat, lng, r)
            if osm:
                sources_used.append(f"osm:{r}km")
                collected.extend(self._cache_osm_spots(osm))

            if len(collected) >= target_count:
                break
        return collected, sources_used

    # -------------------------
    # Cache OSM results
    # -------------------------
    def _cache_osm_spots(self, osm_spots):
        collected = []
        for s in osm_spots:
            if "lat" in s and "lon" in s:
                spot = {
                    "id": s.get("id"),
                    "name": s.get("tags", {}).get("name", "OSM Parking"),
                    "latitude": s["lat"],
                    "longitude": s["lon"],
                    "source": "osm",
                }
                collected.append(spot)
        return collected

    # -------------------------
    # Build response
    # -------------------------
    def _build_response(self, request, spots, radius_km, source, limit):
        if not spots:
            return Response({"message": "No spots found"}, status=404)

        if isinstance(spots[0], ParkingSpot):
            serialized = ParkingSpotSerializer(spots, many=True).data
        else:
            serialized = spots[:limit]

        return Response({
            "count": len(serialized),
            "radius_km": radius_km,
            "source": source,
            "spots": serialized,
            "within_radius": len(spots),
            "message": "Parking spots found"
        })

    # ----------------
    # Additional Helpers
    # ----------------

    def _parse_params(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        if not lat or not lng:
            return Response({"error": "Latitude and longitude are required."}, status=400), None, None, None
        try:
            lat, lng = float(lat), float(lng)
        except ValueError:
            return Response({"error": "Invalid coordinates."}, status=400), None, None, None
        radius_km = float(request.query_params.get("radius", 200))
        radius_km = min(radius_km, settings.PARKING.get("MAX_RADIUS_KM", 200))
        limit = int(request.query_params.get("limit", 60))
        return lat, lng, radius_km, limit

    def _save_to_cache(self, key, spots):
        ids = [s.id for s in spots]
        cache.set(key, ids, timeout=settings.PARKING.get(
            "CACHE_TTL_SECONDS", 3600))
        logger.info("Cached %d OSM spots (key=%s)", len(spots), key)

    def _broadcast_ws(self, spots):
        try:
            for s in spots[:10]:
                send_websocket_update(s)
            logger.info("Broadcasted %d spots to WS", min(10, len(spots)))
        except Exception:
            logger.exception("WS broadcast failed (non-fatal)")

    def _notify_user(self, request, count: int, radius_km: float, source: str = "database"):
        if count > 0:
            title = "Nearby Parking Found 🚗"
            body = f"{count} parking spots found within {int(radius_km)} km ({source})."
        else:
            title = "No Parking Nearby ❌"
            body = f"No parking spots found within {int(radius_km)} km."

        if getattr(request, "user", None) and request.user.is_authenticated:
            try:
                send_notification_async.delay(request.user.id, title, body)
            except Exception as e:
                logger.exception("Celery task dispatch failed: %s", e)
                Notification.objects.create(
                    user=request.user,
                    title=title,
                    body=body,
                    type="private",
                    status="pending",
                    delivered=False,
                    sent_at=timezone.now(),
                )
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

    def _get_osm_import_user(self):
        username = settings.PARKING.get("OSM_IMPORT_USERNAME")
        if not username:
            return None
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @transaction.atomic
    def _cache_osm_spots(self, results: List[Dict]) -> List[ParkingSpot]:
        """
        Idempotently store OSM results in DB.
        - Avoids NOT NULL created_by errors by assigning a service user if required.
        """
        created_by = self._get_osm_import_user()
        objs: List[ParkingSpot] = []

        for r in results:
            defaults = {
                "name": r.get("name") or "Unnamed Parking",
                "latitude": r["lat"],
                "longitude": r["lng"],
                "is_available": True,
                "is_active": True,
                "is_archived": False,
                "source": "osm",
            }
            if hasattr(ParkingSpot, "created_by") and not ParkingSpot._meta.get_field("created_by").null:
                defaults["created_by"] = created_by

            spot, _ = ParkingSpot.objects.update_or_create(
                external_id=str(r["id"]),
                defaults=defaults,
            )
            objs.append(spot)
        return objs


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
