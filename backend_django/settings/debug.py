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

DATABASES = {
    'default': {
    #SQLITE
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / 'db.sqlite3',
    # POSTGRESQL
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": "db",  # "db" set in docker-compose.yml
        "PORT": 5432,  # default postgres port
    }
}

REDIS_HOST = "files"