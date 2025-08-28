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

def bucket_key(lat: float, lng: float, radius_km: float, precision: int = 3) -> str:
    return f"osm:{round(lat, precision)}:{round(lng, precision)}:{int(radius_km)}"

def build_overpass_query(lat: float, lng: float, radius_km: float) -> str:
    radius_m = int(radius_km * 1000)
    return f"""
    [out:json][timeout:{settings.PARKING["OVERPASS_TIMEOUT_SECONDS"]}];
    (
      node["amenity"="parking"](around:{radius_m},{lat},{lng});
      way["amenity"="parking"](around:{radius_m},{lat},{lng});
      relation["amenity"="parking"](around:{radius_m},{lat},{lng});
    );
    out center;
    """

def parse_overpass_json(data: Dict) -> List[Dict]:
    elements = data.get("elements", []) or []
    results: List[Dict] = []
    for el in elements:
        tags = el.get("tags", {}) or {}
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        results.append({
            "id": str(el.get("id")),
            "name": tags.get("name", "Unnamed Parking"),
            "lat": float(lat),
            "lng": float(lon),
            "tags": tags,
        })
    return results

def query_overpass_any(lat: float, lng: float, radius_km: float) -> List[Dict]:
    """Try mirrors. Return empty list on failure (no exceptions)."""
    query = build_overpass_query(lat, lng, radius_km)
    for url in settings.PARKING["OVERPASS_ENDPOINTS"]:
        try:
            # Courtesy small pause to avoid hammering mirrors
            time.sleep(0.3)
            resp = requests.post(url, data={"data": query},
                                 timeout=settings.PARKING["OVERPASS_TIMEOUT_SECONDS"])
            resp.raise_for_status()
            return parse_overpass_json(resp.json())
        except requests.exceptions.RequestException as e:
            logger.warning("Overpass failed on %s (r=%.1fkm): %s", url, radius_km, e)
            continue
    logger.error("All Overpass mirrors failed for r=%.1fkm", radius_km)
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
