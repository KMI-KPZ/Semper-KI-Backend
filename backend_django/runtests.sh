#!/bin/bash
# This is an entry point override for tests
pwd
gunicorn --bind 0.0.0.0:8000 backend_django.wsgi --reload --env DJANGO_SETTINGS_MODULE=backend_django.settings.production &
sleep 5
cd backend_django
python ../manage.py test 