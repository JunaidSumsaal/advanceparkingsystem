import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.user = self.scope["user"]
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.channel_layer.group_add("public_notifications", self.channel_name)

            await self.accept()

    async def disconnect(self, close_code):
        """Remove from group on disconnect."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard("public_notifications", self.channel_name)

    async def receive(self, text_data):
        """Handle client requests (fetch unread, mark read, etc.)."""
        data = json.loads(text_data)
        action = data.get("action")

        if action == "fetch_unread":
            notifications = await self.fetch_unread_notifications(self.user.id)
            await self.send(text_data=json.dumps({
                "type": "unread_notifications",
                "notifications": notifications,
            }))

        elif action == "mark_read":
            notif_id = data.get("id")
            ok = await self.mark_as_read(notif_id)
            await self.send(text_data=json.dumps({
                "type": "mark_read",
                "id": notif_id,
                "success": ok,
            }))

        else:
            await self.send(text_data=json.dumps({"echo": data}))

    async def send_notification(self, event):
        """Send real-time notifications pushed from backend tasks/signals."""
        notification_data = event["data"]
        await self.send(text_data=json.dumps(notification_data))

    # DB OPERATIONS
    @database_sync_to_async
    def fetch_unread_notifications(self, user_id):
        """Fetch unread notifications and serialize them."""
        qs = Notification.objects.filter(
            user_id=user_id, is_read=False).order_by("-sent_at")
        return NotificationSerializer(qs, many=True).data

    @database_sync_to_async
    def mark_as_read(self, notification_id):
        """Mark a notification as read."""
        try:
            notif = Notification.objects.get(id=notification_id)
            notif.is_read = True
            notif.read_at = timezone.now()
            notif.save(update_fields=["is_read", "read_at"])
            return True
        except Notification.DoesNotExist:
            return False
