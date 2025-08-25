import random
from datetime import timedelta
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from notifications.tasks import send_notification_async, booking_reminder_task
from notifications.models import PushSubscription
from notifications.utils import send_web_push
from .utils import calculate_distance, send_websocket_update
from .models import ParkingSpot, Booking, ParkingFacility

User = get_user_model()

@receiver(post_save, sender=ParkingFacility)
def facility_archived_cascade(sender, instance, **kwargs):
    if instance.is_active:
        return

    spots = ParkingSpot.objects.filter(facility=instance, is_active=True)
    total_cancelled = 0

    for spot in spots:
        spot.is_active = False
        spot.save(update_fields=["is_active"])

        for booking in Booking.objects.filter(parking_spot=spot, is_active=True):
            booking.is_active = False
            booking.end_time = booking.end_time or booking.start_time
            booking.save(update_fields=["is_active", "end_time"])
            total_cancelled += 1

            send_notification_async.delay(
                booking.user_id,
                "Booking Cancelled",
                f"Your booking for {spot.name} was cancelled because the facility was archived.",
                "general",
            )

    if total_cancelled > 0:
        recipients = [instance.provider] + list(instance.attendants.all())
        for r in recipients:
            send_notification_async.delay(
                r.id,
                "Facility Archived",
                f"Facility {instance.name} archived. {total_cancelled} active bookings were cancelled.",
                "general",
            )

# -------- Spot archived -> cancel bookings --------
@receiver(post_save, sender=ParkingSpot)
def spot_archived_cancel(sender, instance, **kwargs):
    if instance.is_active:
        return

    active = Booking.objects.filter(parking_spot=instance, is_active=True)
    for booking in active:
        booking.is_active = False
        booking.end_time = booking.end_time or booking.start_time
        booking.save(update_fields=["is_active", "end_time"])

        send_notification_async.delay(
            booking.user_id,
            "Booking Cancelled",
            f"Your booking for {instance.name} was cancelled because the spot was archived.",
            "general",
        )

    if active.exists():
        recipients = [instance.provider]
        if instance.facility:
            recipients += list(instance.facility.attendants.all())
        for r in recipients:
            send_notification_async.delay(
                r.id,
                "Spot Archived",
                f"Spot {instance.name} archived. {active.count()} active bookings were cancelled.",
                "general",
            )

# -------- Spot becomes available --------
@receiver(pre_save, sender=ParkingSpot)
def spot_availability_broadcast(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = ParkingSpot.objects.get(pk=instance.pk)
    except ParkingSpot.DoesNotExist:
        return

    if old.is_available or not instance.is_available:
        return

    # Push to nearby subscribers
    subs = PushSubscription.objects.select_related("user").all()
    for sub in subs:
        profile = getattr(sub.user, "profile", None)
        if not profile:
            continue
        dist = calculate_distance(float(instance.latitude), float(instance.longitude),
                                  float(profile.latitude), float(profile.longitude))
        if dist <= getattr(profile, "search_radius_km", 2.0):
            send_web_push(sub, "🚗 Parking Spot Available", f"{instance.name} is now free!")

    # In-app: send 2-3 random available spots (simple v1; later filter by location)
    available_ids = list(
        ParkingSpot.objects.filter(is_available=True).values_list("id", flat=True)[:20]
    )
    sample_ids = random.sample(available_ids, min(len(available_ids), 3)) if available_ids else []
    for user_id in User.objects.values_list("id", flat=True):
        send_notification_async.delay(
            user_id,
            "🚗 Spots Available Nearby",
            "Good news! A few spots are open near you. Book now.",
            "spot_available",
            {"spot_ids": sample_ids},
        )

    # Realtime WS broadcast
    send_websocket_update(instance)

# -------- Booking created -> confirmations & reminders --------
@receiver(post_save, sender=Booking)
def booking_notifications(sender, instance, created, **kwargs):
    if not created:
        return

    send_notification_async.delay(
        instance.user_id,
        "Booking Confirmed",
        f"You booked {instance.parking_spot.name}. Safe driving!",
        "booking_created",
        {"spot_id": instance.parking_spot_id},
    )

    # quick reminder in 30 minutes
    booking_reminder_task.apply_async(args=[instance.id], countdown=30 * 60)

    # scheduled reminder 30 minutes before start
    if instance.start_time:
        eta = instance.start_time - timedelta(minutes=30)
        if eta > timezone.now():
            booking_reminder_task.apply_async(args=[instance.id], eta=eta)
