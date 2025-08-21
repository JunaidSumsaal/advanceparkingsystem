from django.contrib import admin
from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import metrics_view
from notifications.views import NotificationViewSet, PushSubscriptionViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'push-subscriptions', PushSubscriptionViewSet, basename='push-subscriptions')

urlpatterns = [
    path('portal/admin/', admin.site.urls),
    path('', include('django_prometheus.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/parking/', include('parking.urls')),
    path('api/notifications/', include('notifications.urls')),
    path("api/metrics/", metrics_view, name="metrics"),
    path('api/dashboard/', include('dashboard.urls')),
] + router.urls
