from django.db import models
from django.conf import settings


class PushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    endpoint = models.TextField()
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Push Subscription for {self.user.username}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("spot_available", "Spot Available"),
        ("booking_reminder", "Booking Reminder"),
        ("booking_created", "Booking Created"),
        ("general", "General"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(
        max_length=50, default="general", choices=NOTIFICATION_TYPES
    )

    sent_at = models.DateTimeField(null=True, blank=True)
    delivered = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default="pending")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    extra = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"{self.title} -> {self.user.username}"
        return f"{self.title} (public parent)"

    # Helpers
    @property
    def is_parent(self):
        return self.user is None and self.is_public

    @property
    def delivered_children_count(self):
        return self.children.filter(delivered=True).count()

    @property
    def total_children_count(self):
        return self.children.count()

    @property
    def completion_rate(self):
        total = self.total_children_count
        return (self.delivered_children_count / total) if total > 0 else 0


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    push_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    newsletter_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"


class NotificationTemplate(models.Model):
    EVENT_CHOICES = [
        ("spot_available", "Spot Available"),
        ("booking_reminder", "Booking Reminder"),
        ("booking_created", "Booking Created"),
        ("booking_ended", "Booking Ended"),
        ("general", "General"),
    ]

    event_type = models.CharField(
        max_length=50, choices=EVENT_CHOICES, unique=True)
    title_template = models.CharField(max_length=255)
    body_template = models.TextField()

    def render(self, context: dict) -> dict:
        title = self.title_template.format(**context)
        body = self.body_template.format(**context)
        return {"title": title, "body": body}
