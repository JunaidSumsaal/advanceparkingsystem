from django.contrib import admin
from .models import ParkingFacility, ParkingSpot, Booking, SpotAvailabilityLog

@admin.register(ParkingFacility)
class ParkingFacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "capacity", "latitude", "longitude", "created_at")
    search_fields = ("name", "provider__username")
    list_filter = ("provider",)

@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ("name", "facility", "provider", "spot_type", "price_per_hour", "is_available")
    list_filter = ("facility", "spot_type", "is_available")
    search_fields = ("name", "facility__name", "provider__username")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "parking_spot", "start_time", "end_time", "is_active")
    list_filter = ("is_active", "parking_spot__facility")
    search_fields = ("user__username", "parking_spot__name")

@admin.register(SpotAvailabilityLog)
class SpotAvailabilityLogAdmin(admin.ModelAdmin):
    list_display = ("parking_spot", "timestamp", "is_available", "changed_by")
    list_filter = ("is_available", "parking_spot__facility")
