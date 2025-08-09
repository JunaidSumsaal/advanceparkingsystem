from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import ParkingSpot
from .utils import send_spot_available_notification, send_websocket_update

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
