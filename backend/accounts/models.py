from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('driver', 'Driver'),
        ('provider', 'Provider'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='driver')
    default_radius_km = models.DecimalField(max_digits=4, decimal_places=1, default=2.0)  # adjustable radius

    def __str__(self):
        return f"{self.username} ({self.role})"
