from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_websocket_update(spot):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "parking_updates",
        {
            "type": "parking_update",
            "data": {
                "id": spot.id,
                "name": spot.name,
                "latitude": spot.latitude,
                "longitude": spot.longitude,
                "is_available": spot.is_available
            }
        }
    )

