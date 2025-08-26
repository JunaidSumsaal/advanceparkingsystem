import json
import logging
from django.conf import settings
from pywebpush import webpush, WebPushException
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from .serializers import NotificationSerializer
from geopy.distance import geodesic

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


def broadcast_ws_public(payload: dict):
    """
    Broadcast a payload to the global 'public_notifications' group.
    Used for public spots with no provider.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "public_notifications",
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


def within_radius(user_lat, user_lon, spot_lat, spot_lon, radius_km=10):
    if not user_lat or not user_lon:
        return False
    distance = geodesic((user_lat, user_lon), (spot_lat, spot_lon)).km
    return distance <= radius_km, distance


def get_distance_km(coord1, coord2):
    """Return distance in KM between two (lat, lon) tuples."""
    try:
        return geodesic(coord1, coord2).km
    except Exception as e:
        logger.error(f"Distance calc failed: {e}")
        return None


def queue_notification(user, title, body, ntype="general"):
    """
    Creates a Notification row instead of sending directly.
    """
    return Notification.objects.create(
        user=user,
        title=title,
        body=body,
        type=ntype,
        status="pending"
    )
