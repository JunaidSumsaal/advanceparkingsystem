import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification
from django.utils import timezone
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.group_name = f"user_{self.scope['user'].id}"

            await self.channel_layer.group_add(self.group_name, self.channel_name)

            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({"echo": data}))

    async def send_notification(self, event):
        """
        This method is used to send the actual notification to the user.
        The event should contain a 'data' field with the notification content.
        """
        notification_data = event["data"]
        
        await self.send(text_data=json.dumps({
            "id": notification_data["id"],
            "title": notification_data["title"],
            "body": notification_data["body"],
            "type": notification_data["type"],
            "sent_at": notification_data["sent_at"],
            "is_read": notification_data["is_read"],
            "read_at": notification_data["read_at"],
        }))
    
    @database_sync_to_async
    def fetch_notifications(self, user_id):
        """
        This method fetches the notifications from the database for the user.
        """
        notifications = Notification.objects.filter(user_id=user_id, is_read=False).order_by('-sent_at')
        return notifications.values("id", "title", "body", "type", "sent_at", "is_read", "read_at")

    @database_sync_to_async
    def mark_as_read(self, notification_id):
        """
        This method updates the notification as read.
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
