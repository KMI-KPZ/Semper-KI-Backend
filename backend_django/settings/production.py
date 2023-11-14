"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Further settings for production mode
"""

from .base import *

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DEBUG=False
PRODUCTION=True
BACKEND_SETTINGS= "production"

# for nginx
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_DOMAIN = '.semper-ki.org' 


REDIS_HOST = "files-prod"
CELERY_BROKER_URL = "redis://:"+REDIS_PASSWORD+"@files-prod:6380/0"
CELERY_RESULT_BACKEND = "redis://:"+REDIS_PASSWORD+"@files-prod:6380/0"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://:"+REDIS_PASSWORD+"@files-prod:6380/0",
    }
}