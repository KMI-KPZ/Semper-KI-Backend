#!/bin/bash
# This is an entry point override for tests
pwd
gunicorn --bind 0.0.0.0:8000 backend_django.asgi --reload --env DJANGO_SETTINGS_MODULE=backend_django.settings.production --capture-output --log-level debug -k uvicorn.workers.UvicornWorker --workers 16 --threads 16 &
sleep 5
cd backend_django
export DJANGO_SETTINGS_MODULE=backend_django.settings.production
python ../manage.py test 