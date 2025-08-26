from django.db import models
from django.conf import settings
from django.utils import timezone
from parking.utils import notify_spot_available
from django.core.validators import MinValueValidator, MaxValueValidator


class ActiveFacilityManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class ActiveSpotManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class ParkingFacility(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="facilities",
        limit_choices_to={"role": "provider"}
    )
    name = models.CharField(max_length=255)
    capacity = models.IntegerField(blank=True, null=True, default=0)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )
    address = models.CharField(max_length=500, blank=True, null=True)
    attendants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_facilities",
        blank=True,
        limit_choices_to={"role": "attendant"}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    objects = ActiveFacilityManager()
    active = ActiveManager()
    all_objects = models.Manager()

    def soft_delete(self):
        self.is_active = False
        self.save(update_fields=["is_active"])

    def restore(self):
        self.is_active = True
        self.save(update_fields=["is_active"])

    def __str__(self):
        provider_name = getattr(self.provider, 'username', 'Unknown')
        return f"{self.name} ({provider_name})"

    @property
    def available_spots(self):
        return self.spots.filter(is_available=True, is_archived=False).count()

    class Meta:
        indexes = [
            models.Index(fields=['latitude', 'longitude'])
        ]


class ParkingSpot(models.Model):
    TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    facility = models.ForeignKey(
        ParkingFacility,
        on_delete=models.CASCADE,
        related_name="spots",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )
    spot_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='public')
    price_per_hour = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    base_price_per_hour = models.DecimalField(
        max_digits=6, decimal_places=2, default=2.0)
    is_dynamic_pricing = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    base_price = models.DecimalField(
        max_digits=6, decimal_places=2, default=100.0)
    price_per_hour = models.DecimalField(
        max_digits=6, decimal_places=2, default=100.0)

    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='provided_spots',
        limit_choices_to={"role": "provider"},
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_spots",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    objects = ActiveSpotManager()
    active = ActiveManager()
    all_objects = models.Manager()
    external_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True,
        help_text="External OSM ID (osm-123456). Null if provider-created."
    )
    source = models.CharField(
        max_length=20,
        choices=[("db", "Database"), ("osm", "OpenStreetMap")],
        default="db"
    )
    def soft_delete(self):
        self.is_active = False
        self.save(update_fields=["is_active"])

    def restore(self):
        self.is_active = True
        self.save(update_fields=["is_active"])

    @property
    def dynamic_price_per_hour(self):
        if not self.is_dynamic_pricing:
            return self.base_price_per_hour

        facility = self.facility
        occupancy = 1 - (facility.available_spots / facility.capacity)
        hour = timezone.now().hour

        price = float(self.base_price_per_hour)

        # demand factor
        if occupancy > 0.7:
            price *= 1.5
        elif occupancy > 0.4:
            price *= 1.2

        # peak hours (7–9am, 5–7pm)
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            price *= 1.3

        return round(price, 2)

    def __str__(self):
        return f"{self.name} ({self.spot_type})"

    class Meta:
        indexes = [
            models.Index(fields=['is_available']),
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["external_id"]),
        ]


class AttendantAssignmentLog(models.Model):
    ACTION_CHOICES = [
        ('assigned', 'Assigned'),
        ('removed', 'Removed'),
    ]

    facility = models.ForeignKey(
        ParkingFacility, on_delete=models.CASCADE, related_name='attendant_logs')
    attendant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendant_logs')
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, related_name='attendant_actions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.performed_by} {self.action} {self.attendant} at {self.facility}"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)

    def end_booking(self):
        """Mark booking as ended, calculate cost, and free the spot."""
        self.is_active = False
        self.end_time = timezone.now()
        self.total_price = self.calculate_total_price()
        self.save()

        # Make spot available again
        self.parking_spot.is_available = True
        self.parking_spot.save()
        notify_spot_available(self.parking_spot)

    def calculate_total_price(self):
        if not self.end_time:
            return None
        duration_hours = (
            self.end_time - self.start_time).total_seconds() / 3600
        return round(duration_hours * (self.parking_spot.price_per_hour or 0), 2)

    def __str__(self):
        return f"Booking: {self.user.username} - {self.parking_spot.name}"


class SpotReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    parking_spot = models.ForeignKey(
        ParkingSpot, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)  # 1–5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'parking_spot')

    def __str__(self):
        return f"Review by {self.user.username} for {self.parking_spot.name}"


class SpotAvailabilityLog(models.Model):
    parking_spot = models.ForeignKey(
        ParkingSpot, on_delete=models.CASCADE, related_name='availability_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField()
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Who updated the availability (system, provider, attendant)"
    )

    def __str__(self):
        return f"{self.parking_spot.name} - {self.is_available} at {self.timestamp}"


class SpotPredictionLog(models.Model):
    parking_spot = models.ForeignKey(
        ParkingSpot, on_delete=models.CASCADE, related_name='predictions')
    probability = models.FloatField()
    predicted_for_time = models.DateTimeField()
    model_version = models.CharField(max_length=50, default='v1')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['parking_spot', 'predicted_for_time']),
        ]

    def __str__(self):
        return f"Pred for {self.parking_spot.id} @ {self.predicted_for_time} p={self.probability:.2f}"


class ModelEvaluationLog(models.Model):
    auc_score = models.FloatField()
    brier_score = models.FloatField()
    tolerance_seconds = models.IntegerField(default=120)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Eval @ {self.evaluated_at:%Y-%m-%d %H:%M} | AUC={self.auc_score:.3f} Brier={self.brier_score:.3f}"


class SpotPriceLog(models.Model):
    parking_spot = models.ForeignKey(
        ParkingSpot, on_delete=models.CASCADE, related_name="price_logs")
    old_price = models.DecimalField(max_digits=6, decimal_places=2)
    new_price = models.DecimalField(max_digits=6, decimal_places=2)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parking_spot.name} {self.old_price} -> {self.new_price} @ {self.updated_at}"


class ArchiveReport(models.Model):
    PERIOD_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.period})"
