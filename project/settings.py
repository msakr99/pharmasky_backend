"""
Django settings for PharmaSky project.

This file loads the appropriate settings module based on the DJANGO_SETTINGS_MODULE environment variable.
For development, staging, and production environments, use:
- project.settings.development
- project.settings.staging  
- project.settings.production

Defaults to development if no environment is specified.
"""

import os
import environ

# Initialize environment variables
env = environ.Env()

# Get the settings environment
SETTINGS_ENV = env('DJANGO_SETTINGS_ENV', default='development')

# Import appropriate settings based on environment
if SETTINGS_ENV == 'production':
    from .settings.production import *
elif SETTINGS_ENV == 'staging':
    from .settings.staging import *
else:
    from .settings.development import *

