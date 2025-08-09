from django.db import models
from django.conf import settings

class ParkingSpot(models.Model):
    TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    spot_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='public')
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provided_spots')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.spot_type})"

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Booking: {self.user.username} - {self.parking_spot.name}"

class SpotReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)  # 1–5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.parking_spot.name}"

class SpotAvailabilityLog(models.Model):
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, related_name='availability_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField()

    def __str__(self):
        return f"{self.parking_spot.name} - {self.is_available} at {self.timestamp}"
