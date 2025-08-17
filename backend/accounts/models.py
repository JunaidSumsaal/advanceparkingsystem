from django.conf import settings
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import uuid


class User(AbstractUser):
    ROLE_CHOICES = [
        ('driver', 'Driver'),         # End-user looking for parking
        ('provider', 'Provider'),     # Parking spot owner / building manager
        ('admin', 'Admin'),           # System admin (non-superuser but elevated permissions)
        ('attendant', 'Attendant'),   # Parking lot attendant
        ('guest', 'Guest'),           # Limited access
        ('superuser', 'Superuser'),   # Full system control (maps to is_superuser=True)
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='driver',
        db_index=True
    )
    default_radius_km = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=2.0,
        help_text="Default search radius in kilometers for nearby parking"
    )

    contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact phone number (for providers/attendants)"
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Company or facility name (for providers)"
    )

    def clean(self):
        if self.default_radius_km <= 0:
            raise ValidationError("Search radius must be greater than 0 km.")

    def save(self, *args, **kwargs):
        # Sync role with built-in Django permissions
        if self.role == 'superuser':
            self.is_superuser = True
            self.is_staff = True
        elif self.role == 'admin':
            self.is_staff = True
            self.is_superuser = False
        else:
            # Non-admin roles shouldn't have staff/superuser perms
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)

    # Role-based helpers
    def is_provider(self):
        return self.role == 'provider'

    def is_driver(self):
        return self.role == 'driver'

    def is_attendant(self):
        return self.role == 'attendant'

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]

class AuditLog(models.Model):
    ACTIONS = [
        ("login", "Login"),
        ("logout", "Logout"),
        ("booking_create", "Booking Created"),
        ("booking_cancel", "Booking Cancelled"),
        ("spot_update", "Spot Updated"),
        ("facility_update", "Facility Updated"),
        ("attendant_assignment", "Attendant Assignment"),
        ("notification_sent", "Notification Sent"),
        ("payment", "Payment"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=50, choices=ACTIONS, default="other")
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} -> {self.action} @ {self.timestamp}"

