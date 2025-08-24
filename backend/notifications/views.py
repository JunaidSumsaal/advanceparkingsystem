from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from accounts.utils import log_action
from rest_framework.decorators import action
from .models import PushSubscription, Notification, EmailPreference
from .serializers import PushSubscriptionSerializer, NotificationSerializer, EmailPreferenceSerializer
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
class PushSubscriptionCreateView(generics.CreateAPIView):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        log_action(self.request.user, "subscribe_push", "User subscribed to push notifications", self.request)
        
class PushSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = PushSubscription.objects.all()
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        log_action(self.request.user, "list_push_subscriptions", "User listed push subscriptions", self.request)
        return PushSubscription.objects.filter(user=self.request.user).order_by('-created_at')

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

 
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):
        log_action(self.request.user, "view_notifications", "User viewed notifications", self.request)
        return Notification.objects.filter(user=self.request.user).order_by("-sent_at")

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread": count})

    @action(detail=True, methods=["patch"])
    def read(self, request, pk=None):
        notif = self.get_queryset().filter(pk=pk).first()
        if not notif:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not notif.is_read:
            notif.is_read = True
            notif.read_at = timezone.now()
            notif.save(update_fields=["is_read","read_at"])
        return Response(NotificationSerializer(notif).data)
    
    @action(detail=True, methods=["patch"])
    def unread(self, request, pk=None):
        notif = self.get_queryset().filter(pk=pk).first()
        if not notif:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if notif.is_read:
            notif.is_read = False
            notif.read_at = None
            notif.save(update_fields=["is_read", "read_at"])
        return Response(NotificationSerializer(notif).data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        qs = self.get_queryset().filter(is_read=False)
        now = timezone.now()
        qs.update(is_read=True, read_at=now)
        return Response({"updated": qs.count()})

class EmailPreferenceUpdateView(generics.UpdateAPIView):
    serializer_class = EmailPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination

    def get_object(self):
        log_action(self.request.user, "update_email_preferences", "User updated email preferences", self.request)
        return EmailPreference.objects.get_or_create(user=self.request.user)[0]

class UnsubscribeNotificationView(generics.DestroyAPIView):
    queryset = PushSubscription.objects.all()
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination

    def get_object(self):
        log_action(self.request.user, "unsubscribe_push", "User unsubscribed from push notifications", self.request)
        return PushSubscription.objects.get(user=self.request.user)

class NotificationHistoryView(generics.ListAPIView):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):
        log_action(self.request.user, "view_push_history", "User viewed push notification history", self.request)
        return PushSubscription.objects.filter(user=self.request.user)
