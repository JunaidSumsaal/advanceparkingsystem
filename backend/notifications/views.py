from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from .models import PushSubscription, Notification, NotificationPreference
from .serializers import (
    PushSubscriptionSerializer,
    NotificationSerializer,
    NotificationPreferenceSerializer,
)


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# Notifications
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):
        filter_type = self.request.query_params.get("type")
        qs = Notification.objects.filter(
            user=self.request.user).order_by("-sent_at")
        if filter_type:
            qs = qs.filter(type=filter_type)
        return qs

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False).count()
        return Response({"unread": count})

    @action(detail=True, methods=["patch"])
    def read(self, request, pk=None):
        notif = self.get_queryset().filter(pk=pk).first()
        if not notif:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not notif.is_read:
            notif.is_read = True
            notif.read_at = timezone.now()
            notif.save(update_fields=["is_read", "read_at"])
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
        count = qs.update(is_read=True, read_at=now)
        return Response({"updated": count})


# Push Subscriptions
class PushSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):
        return PushSubscription.objects.filter(user=self.request.user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        sub, _ = PushSubscription.objects.get_or_create(
            user=request.user,
            endpoint=request.data["endpoint"],
            defaults={
                "p256dh": request.data["keys"]["p256dh"],
                "auth": request.data["keys"]["auth"],
            },
        )
        return Response({"message": "Subscription saved"})


# Notification Preferences
class NotificationPreferenceUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = NotificationPreference.objects.get_or_create(
            user=self.request.user)
        return obj
