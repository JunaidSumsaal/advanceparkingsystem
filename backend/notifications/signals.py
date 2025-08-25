from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from notifications.tasks import send_notification_async, booking_reminder_task
from parking.models import ParkingSpot, Booking

@receiver(pre_save, sender=ParkingSpot)
def spot_available_signal(sender, instance, **kwargs):
    if not instance.pk:
        return
    old_instance = ParkingSpot.objects.get(pk=instance.pk)
    if not old_instance.is_available and instance.is_available:
        send_notification_async.delay(
            instance.provider_id,
            "🚗 Parking Spot Available!",
            f"{instance.name} is now free.",
            "spot_available",
            extra={"spot_id": instance.id},
        )

@receiver(post_save, sender=Booking)
def booking_created_signal(sender, instance, created, **kwargs):
    if created:
        send_notification_async.delay(
            instance.user_id,
            "✅ Booking Confirmed",
            f"You booked {instance.parking_spot.name}. Safe driving!",
            "booking_created",
            {"spot_id": instance.parking_spot_id},
        )
        # Reminder in 30 minutes
        booking_reminder_task.apply_async(args=[instance.id], countdown=30*60)
