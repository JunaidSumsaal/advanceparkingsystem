from rest_framework import generics, permissions
from .models import PushSubscription, Notification, EmailPreference
from .serializers import PushSubscriptionSerializer, NotificationSerializer, EmailPreferenceSerializer

class PushSubscriptionCreateView(generics.CreateAPIView):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-sent_at')

class EmailPreferenceUpdateView(generics.UpdateAPIView):
    serializer_class = EmailPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return EmailPreference.objects.get_or_create(user=self.request.user)[0]

class PushSubscriptionListView(generics.ListAPIView):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PushSubscription.objects.filter(user=self.request.user).order_by('-created_at')