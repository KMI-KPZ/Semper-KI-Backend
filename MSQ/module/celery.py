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
broker_url = os.getenv("CELERY_BROKER_URL")
backend_url = os.getenv("CELERY_RESULT_BACKEND")

app = Celery(
    'module',
    broker=broker_url,
    backend=backend_url,
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
)

app.autodiscover_tasks()
app.config_from_object("MSQ.module.celery_config")

if __name__ == '__main__':
    app.start()