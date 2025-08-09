from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import logging

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

