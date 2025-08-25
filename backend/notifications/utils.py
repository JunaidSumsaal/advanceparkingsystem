import json
import logging
from django.conf import settings
from pywebpush import webpush, WebPushException
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger(__name__)


def broadcast_ws_to_user(user_id, notification: Notification):
    """
    Broadcast a notification object to the user's WebSocket group.
    Always serialized via NotificationSerializer for consistency.
    """
    channel_layer = get_channel_layer()
    payload = NotificationSerializer(notification).data
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {"type": "send_notification", "data": payload},
    )


def send_web_push(subscription, payload: dict):
    """Send a web push to a single subscription."""
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
            },
            data=json.dumps(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_CLAIM_SUB},
            ttl=60,
        )
        return True, None
    except WebPushException as e:
        logger.error(f"WebPush failed for {subscription.id}: {e}")
        return False, str(e)
