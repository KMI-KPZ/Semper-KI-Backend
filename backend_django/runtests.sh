#!/bin/bash
pwd
gunicorn --bind 0.0.0.0:8000 backend_django.wsgi --reload &
sleep 5
cd backend_django
python ../manage.py test