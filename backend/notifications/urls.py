from django.urls import path
from .views import NotificationHistoryView, PushSubscriptionCreateView, NotificationListView, EmailPreferenceUpdateView, PushSubscriptionListView, UnsubscribeNotificationView

urlpatterns = [
    path('subscribe/', PushSubscriptionCreateView.as_view(), name='subscribe'),
    path('unsubscribe/', UnsubscribeNotificationView.as_view(), name='unsubscribe'),
    path('history/', NotificationHistoryView.as_view(), name='history'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('email-preference/', EmailPreferenceUpdateView.as_view(), name='email-preference'),
    path('subscriptions/', PushSubscriptionListView.as_view(), name='subscriptions'),
]
