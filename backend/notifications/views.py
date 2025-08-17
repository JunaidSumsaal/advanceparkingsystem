from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from accounts.utils import log_action
from .models import PushSubscription, Notification, EmailPreference
from .serializers import PushSubscriptionSerializer, NotificationSerializer, EmailPreferenceSerializer

class PushSubscriptionCreateView(generics.CreateAPIView):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        log_action(self.request.user, "subscribe_push", "User subscribed to push notifications", self.request)
        
class PushSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = PushSubscription.objects.all()
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        sub, created = PushSubscription.objects.get_or_create(
            user=request.user,
            endpoint=request.data['endpoint'],
            defaults={
                'p256dh': request.data['keys']['p256dh'],
                'auth': request.data['keys']['auth']
            }
        )
        log_action(request.user, "push_subscription_created", f"Push subscription created: {sub.endpoint}", request.user.ip_address)
        return Response({"message": "Subscription saved"})

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        log_action(self.request.user, "view_notifications", "User viewed notifications", self.request)
        return Notification.objects.filter(user=self.request.user).order_by('-sent_at')

class EmailPreferenceUpdateView(generics.UpdateAPIView):
    serializer_class = EmailPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        log_action(self.request.user, "update_email_preferences", "User updated email preferences", self.request)
        return EmailPreference.objects.get_or_create(user=self.request.user)[0]

class PushSubscriptionListView(generics.ListAPIView):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        log_action(self.request.user, "list_push_subscriptions", "User listed push subscriptions", self.request)
        return PushSubscription.objects.filter(user=self.request.user).order_by('-created_at')

class UnsubscribeNotificationView(generics.DestroyAPIView):
    queryset = PushSubscription.objects.all()
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        log_action(self.request.user, "unsubscribe_push", "User unsubscribed from push notifications", self.request)
        return PushSubscription.objects.get(user=self.request.user)

class NotificationHistoryView(generics.ListAPIView):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        log_action(self.request.user, "view_push_history", "User viewed push notification history", self.request)
        return PushSubscription.objects.filter(user=self.request.user)
