from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcast_ws_to_user(user_id, payload: dict):
    async_to_sync(get_channel_layer().group_send)(
        f"user_{user_id}",
        {"type": "send_notification", "data": payload},
    )
