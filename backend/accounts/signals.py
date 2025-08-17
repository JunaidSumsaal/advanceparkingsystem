from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .utils import log_action

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_action(user, "login", "User logged in", request)

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    log_action(user, "logout", "User logged out", request)
