#!/bin/bash
# This is an entry point override for migrations
echo "SLEEPING FOR 10 SECONDS"
sleep 10
pwd
export DJANGO_SETTINGS_MODULE=backend_django.settings.production
python manage.py makemigrations
python manage.py makemigrations backend_django
python manage.py migrate backend_django
python manage.py migrate
 
gunicorn --bind 0.0.0.0:8000 backend_django.wsgi --reload --forwarded-allow-ips="*"