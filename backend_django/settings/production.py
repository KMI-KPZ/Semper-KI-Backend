from .base import *

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DEBUG=False

# for nginx
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

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