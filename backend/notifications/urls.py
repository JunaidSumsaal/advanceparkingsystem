from django.urls import path
from .views import PushSubscriptionCreateView, NotificationListView, EmailPreferenceUpdateView, PushSubscriptionListView

urlpatterns = [
    path('push-subscribe/', PushSubscriptionCreateView.as_view(), name='push-subscribe'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('email-preference/', EmailPreferenceUpdateView.as_view(), name='email-preference'),
    path('push-subscriptions/', PushSubscriptionListView.as_view(), name='push-subscriptions'),
]
