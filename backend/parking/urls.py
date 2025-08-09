from django.urls import path
from .views import (
    NearbyPredictionsView, ParkingSpotListCreateView, NearbyParkingSpotsView, BookParkingSpotView,
    NavigateToSpotView, SpotReviewCreateView, SpotAvailabilityLogListView
)
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('spots/', ParkingSpotListCreateView.as_view(), name='parking_spots'),
    path('nearby/', NearbyParkingSpotsView.as_view(), name='nearby_spots'),
    path('book/', BookParkingSpotView.as_view(), name='book_spot'),
    path('navigate/<int:spot_id>/', NavigateToSpotView.as_view(), name='navigate_spot'),
    path('review/', SpotReviewCreateView.as_view(), name='spot_review'),
    path('availability/logs/', SpotAvailabilityLogListView.as_view(), name='availability_logs'),
    path('predictions/nearby/', NearbyPredictionsView.as_view(), name='predictions_nearby'),

] + router.urls
