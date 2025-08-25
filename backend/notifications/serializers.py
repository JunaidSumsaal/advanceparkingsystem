from rest_framework import serializers
from .models import PushSubscription, Notification, NotificationPreference


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ["id", "endpoint", "p256dh", "auth", "created_at"]
        read_only_fields = ["id", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "body",
            "type",
            "sent_at",
            "delivered",
            "status",
            "is_read",
            "read_at",
        ]
        read_only_fields = ["id", "sent_at", "delivered", "status", "read_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ["push_enabled", "email_enabled", "newsletter_enabled"]
