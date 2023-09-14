"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Further settings for debug mode
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
BACKEND_SETTINGS= "debug"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases



REDIS_HOST = "files"
CELERY_BROKER_URL = "redis://:"+REDIS_PASSWORD+"@files:6379/0"
CELERY_RESULT_BACKEND = "redis://:"+REDIS_PASSWORD+"@files:6379/0"
