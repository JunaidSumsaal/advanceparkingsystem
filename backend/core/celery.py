import os
from celery import Celery
from celery.schedules import crontab
import environ

env = environ.Env()
environ.Env.read_env()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "daily-archive-report": {
        "task": "parking.tasks.generate_archive_report_task",
        "schedule": crontab(hour=0, minute=0),
        "args": ("daily",),
    },
    "weekly-archive-report": {
        "task": "parking.tasks.generate_archive_report_task",
        "schedule": crontab(hour=0, minute=0, day_of_week="monday"),
        "args": ("weekly",),
    },
}
