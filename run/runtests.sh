#!/bin/bash
# This is an entry point override for tests
pwd
gunicorn --bind 0.0.0.0:8000 code_General.asgi --reload --env DJANGO_SETTINGS_MODULE=code_General.settings.production --capture-output --log-level debug -k uvicorn.workers.UvicornWorker --workers 16 --threads 16 --timeout 12000 &
sleep 5
cd code_General
export DJANGO_SETTINGS_MODULE=code_General.settings.production
python ../manage.py test 