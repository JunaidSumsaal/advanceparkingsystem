from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import logging
from notifications.models import PushSubscription
from notifications.utils import send_push_notification
from math import radians, sin, cos, sqrt, atan2
from django.utils.timezone import now

logger = logging.getLogger(__name__)

def send_websocket_update(spot):
    channel_layer = get_channel_layer()
    payload = {
        "id": spot.id,
        "name": spot.name,
        "latitude": float(spot.latitude),
        "longitude": float(spot.longitude),
        "is_available": spot.is_available,
        "timestamp": time.time()
    }
    start = time.time()
    async_to_sync(channel_layer.group_send)(
        "parking_updates",
        {
            "type": "parking_update",
            "data": payload
        }
    )
    latency = time.time() - start
    logger.info(f"Queued WS update for spot={spot.id} queue_latency={latency:.4f}s")

def notify_spot_available(spot):
    subscriptions = PushSubscription.objects.all()
    for sub in subscriptions:
        send_push_notification(sub, "Spot Available", f"{spot.name} is now free")

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))