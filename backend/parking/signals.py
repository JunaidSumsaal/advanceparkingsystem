from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import ParkingSpot
from .utils import send_websocket_update
from .models import ParkingSpot, Booking
from notifications.utils import send_push_notification, log_notification_event, send_spot_available_notification
from notifications.models import PushSubscription
from django.utils.timezone import now
from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


@receiver(pre_save, sender=ParkingSpot)
def spot_availability_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    old_instance = ParkingSpot.objects.get(pk=instance.pk)
    if not old_instance.is_available and instance.is_available:
        # Find subscriptions within radius
        subscriptions = PushSubscription.objects.all()
        for sub in subscriptions:
            user_profile = getattr(sub.user, "profile", None)
            if user_profile:
                distance = calculate_distance(
                    float(instance.latitude),
                    float(instance.longitude),
                    float(user_profile.latitude),
                    float(user_profile.longitude)
                )
                if distance <= getattr(user_profile, "search_radius_km", 2):
                    subscription_info = {
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
                    }
                    status = "sent" if send_push_notification(
                        subscription_info,
                        "Parking Spot Available",
                        f"{instance.name} is now free!"
                    ) else "failed"
                    log_notification_event(sub.user, "Parking Spot Available",
                                        f"{instance.name} is now free!",
                                        "spot_available", status)


@receiver(pre_save, sender=ParkingSpot)
def notify_availability_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = ParkingSpot.objects.get(pk=instance.pk)
    except ParkingSpot.DoesNotExist:
        return

    if not old_instance.is_available and instance.is_available:
        send_spot_available_notification(instance)
        send_websocket_update(instance)
