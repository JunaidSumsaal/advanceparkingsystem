import time
import logging
from math import radians, sin, cos, sqrt, atan2
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from notifications.tasks import send_notification_async
from notifications.models import PushSubscription
from notifications.utils import send_web_push

logger = logging.getLogger(__name__)


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
