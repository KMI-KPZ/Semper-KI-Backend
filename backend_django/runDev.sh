#!/bin/bash
# This is an entry point override for migrations
pwd
gunicorn --bind 0.0.0.0:8000 backend_django.wsgi --reload --env DJANGO_SETTINGS_MODULE=backend_django.settings.development