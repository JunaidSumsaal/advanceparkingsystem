import random
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.tasks import send_notification_async
from parking.models import ParkingFacility, ParkingSpot
from .utils import log_action
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def welcome_user_notification(sender, instance, created, **kwargs):
    if created:
        # Welcome
        send_notification_async.delay(
            instance.id,
            title="🎉 Welcome!",
            body="Welcome to the Smart Parking System. Start exploring available spots!",
            type_="welcome",
        )


@receiver(post_save, sender=User)
def password_change_notification(sender, instance, **kwargs):
    if kwargs.get('update_fields') and 'password' in kwargs['update_fields']:
        send_notification_async.delay(
            user_id=instance.id,
            title="🔐 Password Changed",
            body="Your password has been successfully updated. Please contact support if you did not authorize this change.",
            type_="password_change",
        )

# New signal handler for when a provider creates a new attendant
@receiver(post_save, sender=User)
def attendant_created_notification(sender, instance, created, **kwargs):
    if created and instance.role == 'attendant':
        send_notification_async.delay(
            user_id=instance.id,
            title="👋 You're an Attendant now!",
            body="You have been assigned as an attendant. Check your profile for assigned facilities.",
            type_="attendant_assignment",
        )

# New signal handler for when a provider creates a new parking facility
@receiver(post_save, sender=ParkingFacility)
def facility_created_notification(sender, instance, created, **kwargs):
    if created:
        provider = instance.provider
        if provider:
            send_notification_async.delay(
                user_id=provider.id,
                title="🏢 Facility Created",
                body=f"Your new parking facility, '{instance.name}', has been successfully created!",
                type_="facility_creation",
            )


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_action(user, "login", "User logged in", request)


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    log_action(user, "logout", "User logged out", request)
