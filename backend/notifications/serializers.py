from rest_framework import serializers
from .models import PushSubscription, Notification, EmailPreference

class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ['id', 'endpoint', 'p256dh', 'auth']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id","title","body","type","sent_at","delivered","status","is_read","read_at"]
        read_only_fields = ["id","sent_at","delivered","status","read_at"]
        
class NotificationReadSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), required=False)

class EmailPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailPreference
        fields = ['receive_emails']
