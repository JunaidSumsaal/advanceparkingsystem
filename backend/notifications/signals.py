from django.db.models.signals import pre_save
from django.dispatch import receiver
from notifications.utils import send_spot_available_notification
from parking.models import ParkingSpot

@receiver(pre_save, sender=ParkingSpot)
def check_availability_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    old_instance = ParkingSpot.objects.get(pk=instance.pk)
    if not old_instance.is_available and instance.is_available:
        send_spot_available_notification(instance)
