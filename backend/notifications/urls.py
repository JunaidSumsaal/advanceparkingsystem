from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import NotificationHistoryView, PushSubscriptionViewSet, NotificationViewSet, EmailPreferenceUpdateView, UnsubscribeNotificationView

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'subscribe', PushSubscriptionViewSet, basename='subscribe')

urlpatterns = [
    path('unsubscribe/', UnsubscribeNotificationView.as_view(), name='unsubscribe'),
    path('history/', NotificationHistoryView.as_view(), name='history'),
    path('email-preference/', EmailPreferenceUpdateView.as_view(), name='email-preference'),
] + router.urls
