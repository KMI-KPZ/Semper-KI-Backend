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
BACKEND_SETTINGS= "development"

# for nginx
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_DOMAIN = '.semper-ki.org'


REDIS_HOST = "files-dev"