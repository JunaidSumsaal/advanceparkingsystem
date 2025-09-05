from typing import Dict, List
import random
from typing import Dict, List, Tuple
import requests
from django.conf import settings
import time
import logging
from math import radians, sin, cos, sqrt, atan2
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from notifications.tasks import send_notification_async
from notifications.models import PushSubscription
from notifications.utils import send_web_push

logger = logging.getLogger(__name__)


def bucket_key(lat: float, lng: float, radius_km: float, precision: int = 2) -> str:
    """
    Build a cache bucket key for OSM queries.
    Default precision=2 so nearby coords share cache buckets (avoids cache fragmentation).
    """
    key = f"osm:{round(lat, precision)}:{round(lng, precision)}:{int(radius_km)}"
    logger.debug("Generated bucket_key=%s (lat=%.5f, lng=%.5f, r=%.1f km, precision=%d)",
                 key, lat, lng, radius_km, precision)
    return key


def query_overpass_any(lat: float, lng: float, radius_km: float,
                       max_retries: int = 3, base_backoff: int = 2) -> List[Dict]:
    """
    Query OSM Overpass API with endpoint rotation + retries + backoff.
    Returns [] on total failure.
    """
    query = f"""
    [out:json][timeout:{settings.PARKING['OVERPASS_TIMEOUT_SECONDS']}];
    (
      node["amenity"="parking"](around:{int(radius_km*1000)},{lat},{lng});
      way["amenity"="parking"](around:{int(radius_km*1000)},{lat},{lng});
      relation["amenity"="parking"](around:{int(radius_km*1000)},{lat},{lng});
    );
    out center;
    """

    endpoints = settings.PARKING["OVERPASS_ENDPOINTS"].copy()
    random.shuffle(endpoints)  # spread requests across mirrors

    for endpoint in endpoints:
        backoff = base_backoff
        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    endpoint,
                    data={"data": query},
                    timeout=settings.PARKING["OVERPASS_TIMEOUT_SECONDS"]
                )
                resp.raise_for_status()
                data = resp.json()

                results = []
                for el in data.get("elements", []):
                    tags = el.get("tags", {}) or {}
                    latlng = el.get("center") or {
                        "lat": el.get("lat"),
                        "lon": el.get("lon")
                    }
                    if not latlng["lat"] or not latlng["lon"]:
                        continue
                    results.append({
                        "id": str(el["id"]),
                        "name": tags.get("name", "Unnamed Parking"),
                        "lat": float(latlng["lat"]),
                        "lng": float(latlng["lon"]),
                        "tags": tags,
                    })

                logger.info(
                    "Overpass success endpoint=%s radius=%.1fkm → %d results",
                    endpoint, radius_km, len(results)
                )
                return results

            except Exception as e:
                logger.warning(
                    "Overpass failed (attempt %d/%d) endpoint=%s radius=%.1fkm → %s",
                    attempt + 1, max_retries, endpoint, radius_km, e
                )
                time.sleep(backoff)
                backoff *= 2

    logger.error(
        "All Overpass mirrors failed after retries (r=%.1fkm)", radius_km)
    return []


def send_websocket_update(spot):
    channel_layer = get_channel_layer()
    payload = {
        "id": spot.id,
        "name": spot.name,
        "latitude": float(spot.latitude),
        "longitude": float(spot.longitude),
        "is_available": spot.is_available,
        "timestamp": time.time(),
    }
    t0 = time.time()
    async_to_sync(channel_layer.group_send)(
        "parking_updates",
        {"type": "parking_update", "data": payload},
    )
    logger.info("Queued WS update for spot=%s latency=%.4fs",
                spot.id, time.time() - t0)


def notify_spot_available_push(spot):
    # light, best-effort broadcast to all push subscribers (you can filter later)
    for sub in PushSubscription.objects.all():
        send_web_push(sub, "🚗 Spot Available", f"{spot.name} is now free")


def calculate_distance(lat1, lon1, lat2, lon2):
    # Proper Haversine distance (km)
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2) ** 2 + cos(radians(lat1)) * \
        cos(radians(lat2)) * sin(dlon/2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def notify_spot_available(spot):
    for sub in PushSubscription.objects.all():
        send_web_push(sub, "🚗 Spot Available", f"{spot.name} is now free")
    send_notification_async.delay(
        spot.provider_id,
        "Spot Available",
        f"{spot.name} is now available.",
        "spot_available",
        {"spot_id": spot.id}
    )
