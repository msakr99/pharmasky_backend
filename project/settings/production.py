"""
Production settings for PharmaSky project.
"""

from .base import *
import firebase_admin

# Production database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='defaultdb'),
        'USER': env('DB_USER', default='doadmin'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='pharmasky-db-do-user-17921548-0.h.db.ondigitalocean.com'),
        'PORT': env('DB_PORT', default='25060'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
}

# DigitalOcean Spaces Configuration
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='pharmasky-media')
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL', default='https://pharmasky-media.fra1.digitaloceanspaces.com')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='fra1')
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = env('AWS_LOCATION', default='media')

# Production storage configuration
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "default_acl": AWS_DEFAULT_ACL,
            "location": AWS_LOCATION,
            "verify": True,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "signature_version": AWS_S3_SIGNATURE_VERSION,
            "region_name": AWS_S3_REGION_NAME,
            "object_parameters": AWS_S3_OBJECT_PARAMETERS,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3StaticStorage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "default_acl": AWS_DEFAULT_ACL,
            "location": "static",
            "verify": True,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "signature_version": AWS_S3_SIGNATURE_VERSION,
            "region_name": AWS_S3_REGION_NAME,
            "object_parameters": AWS_S3_OBJECT_PARAMETERS,
        },
    },
}

# Update URLs for production
STATIC_URL = f"{AWS_S3_ENDPOINT_URL}/static/"
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_LOCATION}/"

# Production CORS settings
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS', default=[])
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS', default=[])

# Security settings for production
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', default=True)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Session security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Production logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "json": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/pharmasky/production.log",
            "maxBytes": 1024*1024*10,  # 10MB
            "backupCount": 5,
            "formatter": "json",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["mail_admins", "file"],
            "level": "ERROR",
            "propagate": False,
        },
        "pharmasky": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Firebase configuration for production
FIREBASE_CREDENTIALS_PATH = env("FIREBASE_CREDENTIALS", default='/app/firebase-credentials.json')
try:
    FIREBASE_CREDENTIALS = firebase_admin.credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(FIREBASE_CREDENTIALS)
except Exception as e:
    print(f"Firebase initialization failed in production: {e}")

# Celery settings for production
CELERY_BROKER_URL = env("CELERY_BROKER", default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env("CELERY_BACKEND", default='redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'pharmasky',
        'TIMEOUT': 300,
        'VERSION': 1,
    }
}

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@pharmasky.com')

