from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    NearbyPredictionsView,
    NearbyParkingSpotsView,
    NavigateToSpotView,
    SpotPriceLogView,
    SpotReviewCreateView,
    SpotAvailabilityLogListView,
    ParkingFacilityView,
    BookingViewSet,
    trigger_dynamic_pricing,
    ParkingSpotViewSet,
)

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'facilities', ParkingFacilityView, basename='facility')
router.register(r'spots', ParkingSpotViewSet, basename='parking_spot')

urlpatterns = [
    path('nearby/', NearbyParkingSpotsView.as_view(), name='nearby_spots'),
    path('navigate/<int:spot_id>/', NavigateToSpotView.as_view(), name='navigate_spot'),
    path('review/', SpotReviewCreateView.as_view(), name='spot_review'),
    path('availability/logs/', SpotAvailabilityLogListView.as_view(), name='availability_logs'),
    path('predictions/nearby/', NearbyPredictionsView.as_view(), name='predictions_nearby'),
    path("pricing/update/", trigger_dynamic_pricing, name="update_dynamic_pricing"),
    path("pricing/logs/", SpotPriceLogView.as_view(), name="spot_price_logs"),
] + router.urls
