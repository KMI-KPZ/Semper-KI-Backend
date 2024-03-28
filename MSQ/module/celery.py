"""
Part of Semper-KI software

Akshay NS 2023

Contains: Configuration for Celery worker

"""
############################################
from __future__ import absolute_import


import os
from celery import Celery
############################################
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings.base")
from django.conf import settings

broker_url = os.getenv("CELERY_BROKER_URL")
backend_url = os.getenv("CELERY_RESULT_BACKEND")

app = Celery(
    'main',
    broker=broker_url,
    backend=backend_url,
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True
)

#app.config_from_object("MSQ.module.celery_config")

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: ['code_SemperKI'])
#app.autodiscover_tasks()
app.autodiscover_tasks(['MSQ.tasks'])