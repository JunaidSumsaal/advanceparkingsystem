from django.core.mail import send_mail
from django.conf import settings

def send_email_notification(to_email, subject, body):
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
