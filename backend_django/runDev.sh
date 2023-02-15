#!/bin/bash
# This is an entry point override for migrations
pwd
echo "SLEEPING FOR 10 SECONDS"
sleep 10

rm backend_django/migrations/0001_initial.py
export DJANGO_SETTINGS_MODULE=backend_django.settings.development
python manage.py makemigrations
python manage.py makemigrations backend_django
python manage.py migrate backend_django
python manage.py migrate
 
gunicorn --bind 0.0.0.0:8000 backend_django.wsgi --reload --env DJANGO_SETTINGS_MODULE=backend_django.settings.development --capture-output --log-level debug --workers 16 --threads 16