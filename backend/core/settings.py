import json
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

SECRET_KEY = env(
    'SECRET_KEY', default='ef365827fed3b2bbe05aa453f557098e48b9d713517721c6116df666b8e370f443b8214935766de02be228a499573085')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
                         'localhost', 'advanceparkingsystem.onrender.com', 'advanceparkingsystem-backend.onrender.com'])

if DEBUG:
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

CELERY_BROKER_URL = env("CELERY_BROKER_URL",
                        default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND",
                            default="redis://localhost:6379/0")
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_TIME_LIMIT = 30
CELERY_TASK_SOFT_TIME_LIMIT = 20
CELERY_ACCEPT_CONTENT = json.loads(
    env("CELERY_ACCEPT_CONTENT", default='["json"]'))
CELERY_RESULT_SERIALIZER = env("CELERY_RESULT_SERIALIZER", default="json")
CELERY_TASK_SERIALIZER = env("CELERY_TASK_SERIALIZER", default="json")

APPEND_SLASH = False
VAPID_PRIVATE_KEY = env('VAPID_PRIVATE_KEY',
                        default='95d05a8c43ad9b3d9f079995211fac2f188bfa7b')
VAPID_CLAIM_SUB = env(
    'VAPID_CLAIM_SUB', default='mailto:advanceparkingsystem@gmail.com')


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
    'celery',
    'django_celery_beat',
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
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'parking.middleware.PredictionLoggingMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "https://advanceparkingsystem.onrender.com",
    "https://advanceparkingsystem-backend.onrender.com",
]


ROOT_URLCONF = 'core.urls'

AUTH_USER_MODEL = 'accounts.User'

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
ASGI_APPLICATION = "core.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("DB_NAME", default="dummy_db"),
        "USER": env("DB_USER", default="dummy_user"),
        "PASSWORD": env("DB_PASSWORD", default="dummy_password"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}


# if DEBUG:
#     DATABASES = {
#         "default": env.db("SQLITE_URL", default="sqlite:///db.sqlite3")
#     }


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

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
        }
    },
}

if DEBUG:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": "redis://localhost:6379/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            }
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
        "args": (1,),
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

# Email Configuration for Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="dummy@example.com")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="dummy_password")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.example.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')


PARKING = {
    "OVERPASS_ENDPOINTS": [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.openstreetmap.ru/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.nchc.org.tw/api/interpreter"
    ],
    "OVERPASS_TIMEOUT_SECONDS": 60,
    "CACHE_TTL_SECONDS": 60 * 60 * 24,
    "MAX_RADIUS_KM": 500,
    "EXPANSION_RADII_KM": [5, 10, 20, 50, 100, 200],
    "OSM_IMPORT_USERNAME": "osm-import",
    "TARGET_RESULT_COUNT": 40,
}
