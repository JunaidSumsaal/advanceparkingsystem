from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Notification
from .utils import broadcast_ws_public, broadcast_ws_to_user, within_radius
from .tasks import booking_reminder_task
from parking.models import ParkingSpot, Booking
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(pre_save, sender=ParkingSpot)
def spot_available_signal(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_instance = ParkingSpot.objects.get(pk=instance.pk)

    if not old_instance.is_available and instance.is_available:
        # provider-owned spot
        if instance.provider_id:
            # 🔹 Notify provider
            provider_notif = Notification.objects.create(
                user_id=instance.provider_id,
                title="Parking Spot Available! 🚗",
                body=f"{instance.name} is now free.",
                type="spot_available",
                extra={
                    "spot_id": instance.id,
                    "lat": instance.latitude,
                    "lng": instance.longitude,
                    "spot_name": instance.name,
                },
            )
            broadcast_ws_to_user(instance.provider_id, provider_notif)

            # 🔹 Notify nearby users within 10 km
            spot_coords = (instance.latitude, instance.longitude)
            for user in User.objects.exclude(latitude=None).exclude(longitude=None):
                is_near, dist = within_radius(
                    user.latitude, user.longitude,
                    spot_coords[0], spot_coords[1],
                    radius_km=10
                )
                if is_near:
                    notif = Notification.objects.create(
                        user=user,
                        title="Nearby Parking Spot Available 🚗",
                        body=f"{instance.name} is available {dist:.1f} km from you.",
                        type="spot_nearby",
                        extra={
                            "spot_id": instance.id,
                            "lat": instance.latitude,
                            "lng": instance.longitude,
                            "spot_name": instance.name,
                            "distance": dist,
                        },
                    )
                    broadcast_ws_to_user(user.id, notif)

        else:
            # 🔹 Public notification
            public_notif = Notification.objects.create(
                title="Public Spot Available 🚙",
                body=f"{instance.name} is now free.",
                type="spot_available",
                is_public=True,
                extra={
                    "spot_id": instance.id,
                    "lat": instance.latitude,
                    "lng": instance.longitude,
                    "spot_name": instance.name,
                },
            )
            broadcast_ws_public(
                {
                    "title": public_notif.title,
                    "body": public_notif.body,
                    "spot_id": instance.id,
                    "type": public_notif.type,
                    "is_public": True,
                }
            )


@receiver(post_save, sender=Booking)
def booking_created_signal(sender, instance, created, **kwargs):
    if created:
        booking_notif = Notification.objects.create(
            user=instance.user,
            title="✅ Booking Confirmed",
            body=f"You booked {instance.parking_spot.name}. Safe driving!",
            type="booking_created",
            extra={"spot_id": instance.parking_spot_id},
        )
        broadcast_ws_to_user(instance.user_id, booking_notif)

        booking_reminder_task.apply_async(args=[instance.id], countdown=30*60)
