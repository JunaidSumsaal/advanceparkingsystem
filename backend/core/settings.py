import os
import environ
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab
from pythonjsonlogger import jsonlogger

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost'])

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_TIME_LIMIT = 30
CELERY_TASK_SOFT_TIME_LIMIT = 20
CELERY_TASK_SERIALIZER = env('CELERY_TASK_SERIALIZER', default='json')
CELERY_ACCEPT_CONTENT = env.list('CELERY_ACCEPT_CONTENT', default='json')
CELERY_RESULT_SERIALIZER = env('CELERY_RESULT_SERIALIZER', default='json')

APPEND_SLASH = False

VAPID_PRIVATE_KEY = env('VAPID_PRIVATE_KEY', default='95d05a8c43ad9b3d9f079995211fac2f188bfa7b')
VAPID_CLAIM_SUB = env('VAPID_CLAIM_SUB', default='mailto:advanceparkingsystem@gmail.com')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

INSTALLED_APPS = [
    'django_prometheus',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_extensions',
    'corsheaders',
    'channels',
    'accounts',
    'rest_framework_simplejwt.token_blacklist',
    'parking',
    'notifications',
    'dashboard',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware','django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'core.urls'

AUTH_USER_MODEL = 'accounts.User'

ASGI_APPLICATION = "core.asgi.application"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


DATABASES = {
    "default": env.db(
        "DATABASE_URL", 
        default="postgres://username:password@localhost:5432/advanceparkingsystem"
    )
}


if DEBUG:
    DATABASES = {
        "default": env.db("SQLITE_URL", default="sqlite:///db.sqlite3")
    }




AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10, 
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('ACCESS_TOKEN_LIFETIME', 60)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=env.int('REFRESH_TOKEN_LIFETIME', 1440)),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [env("REDIS_URL", default="redis://localhost:6379/0")]},
    },
}

CELERY_BEAT_SCHEDULE = {
    "send-notifications-every-minute": {
        "task": "notifications.tasks.send_pending_notifications",
        "schedule": 60.0,  # every 60 seconds
    },
    "provider-daily-digest": {
        "task": "notifications.tasks.daily_digest_for_provider",
        "schedule": crontab(hour=7, minute=0),
        "args": (1,),  # example provider_id; replace with a beat that loops providers if needed to whoever needs it in the system
    },
}

LOG_LEVEL = env("DJANGO_LOG_LEVEL", default="INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(user)s %(ip)s %(session_id)s",
        },
        "default": {
            "format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
}