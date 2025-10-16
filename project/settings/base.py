"""
Base Django settings for PharmaSky project.
This file contains settings shared across all environments.
"""

import os
from pathlib import Path
import environ
from corsheaders.defaults import default_headers
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ''),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    SECURE_SSL_REDIRECT=(bool, False),
)

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure--pv1n!%sr_ny^-5oqu72ije32z%1cl$qq#24pw&2as#h6o6!mh')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=False)

ALLOWED_HOSTS = env('ALLOWED_HOSTS', default=[])

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "storages",
    "rest_framework",
    "rest_framework.authtoken",
    "phonenumber_field",
    "django_filters",
    "debug_toolbar",
    "rosetta",
    "import_export",
    "drf_spectacular",
    "django_celery_beat",
    "push_notifications",
]

LOCAL_APPS = [
    "core",
    "accounts",
    "profiles",
    "market",
    "offers",
    "finance",
    "shop",
    "ads",
    "invoices",
    "inventory",
    "notifications",
    "ai_agent",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "libraries": {
                "math": "project.templatetags.math",
                "utils": "project.templatetags.utils",
                "admin.urls": "django.contrib.admin.templatetags.admin_urls",
            },
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("ar", _("Arabic")),
    ("en", _("English")),
]

LOCALE_PATHS = (BASE_DIR / "locale",)

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login redirect
LOGIN_REDIRECT_URL = "/"

# DRF Configuration
DEFAULT_RENDERER_CLASSES = [
    "rest_framework.renderers.JSONRenderer",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.views.abstract_paginations.CustomPageNumberPagination",
    "DEFAULT_RENDERER_CLASSES": DEFAULT_RENDERER_CLASSES,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "PAGE_SIZE": 20,
    "ORDERING_PARAM": "o",
    "EXCEPTION_HANDLER": "core.exception_handlers.exception_handler",
    # Rate Limiting for AI Agent
    "DEFAULT_THROTTLE_RATES": {
        "ai_agent_user": "10/minute",  # 10 requests per minute for authenticated users
        "ai_agent_anon": "5/minute",   # 5 requests per minute for anonymous
        "ai_agent_burst": "3/minute",  # Burst protection
    },
}

# API Documentation
SPECTACULAR_SETTINGS = {
    "TITLE": "PharmaSky API",
    "DESCRIPTION": "PharmaSky Backend API Documentation",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
}

# Upload settings
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "project" / "static"]

# Media files (User uploads)
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# CORS Settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + ["X-Timezone", "content-disposition"]
CORS_EXPOSE_HEADERS = ["Content-Disposition"]

# Internationalization admin
ROSETTA_SHOW_AT_ADMIN_PANEL = True

# Push notifications settings
PUSH_NOTIFICATIONS_SETTINGS = {"UPDATE_ON_DUPLICATE_REG_ID": True}

# OpenAI / AI Agent configuration
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
DIGITALOCEAN_AGENT_URL = env('DIGITALOCEAN_AGENT_URL', default='https://api.openai.com/v1')

# Custom application settings
MINIMUM_PHARMACY_INVOICE_SUB_TOTAL = 600
MAX_RETURN_PERIOD_IN_DAYS = 7

