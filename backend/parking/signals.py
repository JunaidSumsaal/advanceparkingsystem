from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from accounts.utils import log_action
from notifications.models import PushSubscription, Notification
from notifications.utils import send_web_push, log_notification_event, send_spot_available_notification
from notifications.tasks import send_notification_async, booking_reminder_task
from .utils import calculate_distance, send_websocket_update
from .models import ParkingSpot, SpotAvailabilityLog, Booking, ParkingFacility


@receiver(post_save, sender=ParkingFacility)
def cascade_archive_spots(sender, instance, **kwargs):
    if not instance.is_active:
        spots = ParkingSpot.objects.filter(facility=instance, is_active=True)
        total_cancelled = 0

        for spot in spots:
            spot.is_active = False
            spot.save()

            active_bookings = Booking.objects.filter(
                parking_spot=spot, is_active=True)
            total_cancelled += active_bookings.count()

            for booking in active_bookings:
                booking.is_active = False
                booking.end_time = booking.end_time or booking.start_time
                booking.save()

                Notification.objects.create(
                    user=booking.user,
                    title="Booking Cancelled",
                    body=f"Your booking for {spot.name} was cancelled because the facility was archived.",
                    type="general",
                    status="sent",
                    delivered=True
                )

                log_action(
                    booking.user,
                    "booking_cancelled_facility_archive",
                    f"Booking for spot {spot.name} cancelled due to facility {instance.name} archive",
                    None
                )

        if total_cancelled > 0:
            Notification.objects.create(
                user=instance.provider,
                title="Facility Archived",
                body=f"Facility {instance.name} archived. {total_cancelled} active bookings were cancelled.",
                type="general",
                status="sent",
                delivered=True
            )
            for attendant in instance.attendants.all():
                Notification.objects.create(
                    user=attendant,
                    title="Facility Archived",
                    body=f"Facility {instance.name} archived. {total_cancelled} active bookings were cancelled.",
                    type="general",
                    status="sent",
                    delivered=True
                )

            log_action(
                instance.provider,
                "facility_archived",
                f"Facility {instance.name} archived. {total_cancelled} bookings cancelled.",
                None
            )


@receiver(post_save, sender=ParkingSpot)
def handle_spot_archive(sender, instance, **kwargs):
    if not instance.is_active:
        active_bookings = Booking.objects.filter(
            parking_spot=instance, is_active=True)
        cancelled_count = active_bookings.count()

        for booking in active_bookings:
            booking.is_active = False
            booking.end_time = booking.end_time or booking.start_time
            booking.save()

            Notification.objects.create(
                user=booking.user,
                title="Booking Cancelled",
                body=f"Your booking for {instance.name} was cancelled because the spot was archived.",
                type="general",
                status="sent",
                delivered=True
            )

            log_action(
                booking.user,
                "booking_cancelled_spot_archive",
                f"Booking for spot {instance.name} cancelled due to spot archive",
                None
            )

        if cancelled_count > 0:
            Notification.objects.create(
                user=instance.provider,
                title="Spot Archived",
                body=f"Spot {instance.name} archived. {cancelled_count} active bookings were cancelled.",
                type="general",
                status="sent",
                delivered=True
            )
            if instance.facility:
                for attendant in instance.facility.attendants.all():
                    Notification.objects.create(
                        user=attendant,
                        title="Spot Archived",
                        body=f"Spot {instance.name} archived. {cancelled_count} active bookings were cancelled.",
                        type="general",
                        status="sent",
                        delivered=True
                    )

            log_action(
                instance.provider,
                "spot_archived",
                f"Spot {instance.name} archived. {cancelled_count} bookings cancelled.",
                None
            )


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
                    status = "sent" if send_web_push(
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


# parking/signals.py (examples)

@receiver(post_save, sender=Booking)
def booking_created(sender, instance, created, **kwargs):
    if created:
        send_notification_async.delay(
            instance.user_id,
            "Booking Confirmed",
            f"You booked {instance.parking_spot.name}. Safe driving!",
            "booking_created",
            {"spot_id": instance.parking_spot_id},
        )
        # optional reminder in 30 minutes
        booking_reminder_task.apply_async(args=[instance.id], countdown=30*60)


@receiver(post_save, sender=ParkingSpot)
def spot_status_changed(sender, instance, **kwargs):
    if instance.is_available:
        # notify subscribers of this spot/provider (simplified to provider)
        send_notification_async.delay(
            instance.provider_id,
            "Spot Available",
            f"{instance.name} is now available.",
            "spot_available",
            {"spot_id": instance.id},
        )
