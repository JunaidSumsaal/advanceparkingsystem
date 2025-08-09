from django.db import models
from django.conf import settings

class PushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    endpoint = models.TextField()
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Push Subscription for {self.user.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('spot_available', 'Spot Available'),
        ('booking_reminder', 'Booking Reminder'),
        ('general', 'General')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(max_length=50, default="general", choices=NOTIFICATION_TYPES)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"{self.title} -> {self.user.username}"

class EmailPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receive_emails = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} Email Pref"
