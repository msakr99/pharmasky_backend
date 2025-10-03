"""
Development settings for PharmaSky project.
"""

from .base import *
import os

# Override DEBUG for development
DEBUG = True

# Development-specific middleware
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Internal IPs for debug toolbar
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Database configuration for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Add browsable API renderer for development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# Development CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://129.212.140.152",
    "https://129.212.140.152",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://129.212.140.152",
    "https://129.212.140.152",
]

# Additional CORS headers for development
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-timezone',
    'content-disposition',
]

# Security headers for development
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Storage configuration for development (local filesystem)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Logging configuration for development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {
            "format": "%(levelname)s %(asctime)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "development.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "pharmasky": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / "logs", exist_ok=True)

# Firebase initialization for development (optional)
try:
    import firebase_admin
    FIREBASE_CREDENTIALS_PATH = env(
        "FIREBASE_CREDENTIALS", 
        default=BASE_DIR / 'pharmasky-2a5a3-firebase-adminsdk-fbsvc-4aa69c05c7.json'
    )
    FIREBASE_CREDENTIALS = firebase_admin.credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(FIREBASE_CREDENTIALS)
except Exception as e:
    print(f"Firebase initialization failed in development: {e}")

# Celery settings for development
CELERY_BROKER_URL = env("CELERY_BROKER", default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env("CELERY_BACKEND", default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

