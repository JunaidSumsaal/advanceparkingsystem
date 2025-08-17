from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, pre_save
from accounts.utils import log_action
from .utils import calculate_distance, send_websocket_update
from .models import ParkingSpot, SpotAvailabilityLog
from notifications.models import PushSubscription
from notifications.utils import send_push_notification, log_notification_event, send_spot_available_notification


@receiver(post_save, sender=ParkingSpot)
def update_facility_capacity_on_create(sender, instance, created, **kwargs):
    """Update facility capacity when a new spot is created."""
    if created and instance.facility:
        facility = instance.facility
        facility.capacity = facility.spots.filter(is_deleted=False).count()
        facility.save()
        log_action(instance.created_by, "spot_created", f"Spot {instance.name} created in facility {facility.name}", instance.created_by.ip_address)


@receiver(pre_delete, sender=ParkingSpot)
def update_facility_capacity_on_delete(sender, instance, **kwargs):
    """Update facility capacity when a spot is deleted."""
    if instance.facility:
        facility = instance.facility
        facility.capacity = facility.spots.filter(is_deleted=False).exclude(id=instance.id).count()
        facility.save()
        log_action(instance.deleted_by, "spot_deleted", f"Spot {instance.name} deleted from facility {facility.name}", instance.deleted_by.ip_address)


@receiver(pre_save, sender=ParkingSpot)
def create_availability_log(sender, instance, **kwargs):
    """Create a SpotAvailabilityLog whenever availability changes."""
    if not instance.pk:
        log_action(instance.created_by, "spot_created", f"Spot {instance.name} created", instance.created_by.ip_address)
        return
    old_instance = ParkingSpot.objects.get(pk=instance.pk)
    if old_instance.is_available != instance.is_available:
        SpotAvailabilityLog.objects.create(
            parking_spot=instance,
            is_available=instance.is_available,
            changed_by=getattr(instance, '_changed_by', None)
        )
        log_action(instance.created_by, "spot_availability_changed", f"Spot {instance.name} availability changed to {instance.is_available}", instance.created_by.ip_address)

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
