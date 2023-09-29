"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Celery handlers for async process calls running in the background
"""

# https://testdriven.io/courses/django-celery/getting-started/

import os
from celery import Celery
from django.conf import settings
from backend_django.settings import set_settings

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_django.settings.debug")# os.environ.get("DJANGO_SETTINGS_MODULE"))

# include this variable into files using Celery
set_settings()
app = Celery('backend_django')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
