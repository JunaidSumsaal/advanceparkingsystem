from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet,
    PushSubscriptionViewSet,
    NotificationPreferenceUpdateView,
    NotificationTypesView,
)

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet,
                basename="notifications")
router.register(r"subscriptions", PushSubscriptionViewSet,
                basename="subscriptions")

urlpatterns = [
    path("preferences/", NotificationPreferenceUpdateView.as_view(),
         name="preferences"),
    path("types/", NotificationTypesView.as_view(),
         name="preferences"),
] + router.urls
