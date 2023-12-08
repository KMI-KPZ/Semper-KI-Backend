"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Further settings for development mode
"""


from .base import *

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DEBUG = False
DEVELOPMENT=True
BACKEND_SETTINGS= "stage"

# for nginx
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_DOMAIN = '.semper-ki.org'

CELERY_BROKER_URL = CELERY_RESULT_BACKEND=  f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0",
    }
}

# CELERY_BROKER_URL = "redis://:"+REDIS_PASSWORD+"@files-dev:6379/0"
# CELERY_RESULT_BACKEND = "redis://:"+REDIS_PASSWORD+"@files-dev:6379/0"
#
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": "redis://:"+REDIS_PASSWORD+"@files-dev:6379/0",
#     }
# }