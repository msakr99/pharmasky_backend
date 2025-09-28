"""
Staging settings for PharmaSky project.
Inherits from production but with some adjustments for staging environment.
"""

from .production import *

# Override some production settings for staging
DEBUG = env('DEBUG', default=False)

# Staging-specific logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
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
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/pharmasky/staging.log",
            "maxBytes": 1024*1024*5,  # 5MB
            "backupCount": 3,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "pharmasky": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Less strict security for staging
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', default=False)
SECURE_HSTS_SECONDS = 0

# Add browsable API for staging
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

