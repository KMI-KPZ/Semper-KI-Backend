"""
Part of Semper-KI software

Akshay NS 2023

Contains: Configuration for Celery worker

"""
############################################
from __future__ import absolute_import
import requests, threading

import os
from celery import Celery
from celery.signals import task_success


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

########################################################################
def request_task(id):
    """
    Communicate to backend, that task is finished

    :param id: The task ID
    :type id: str
    """

    requests.get(f"http://host.docker.internal:8000/private/getResultsLocal/{id}/")


########################################################################
def fire_and_forget(id):
    """
    Send out request but don't await answer

    :param id: The task ID
    :type id: str
    """
    threading.Thread(target=request_task, args=(id,)).start()


########################################################################
@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """
    Gets called after every celery task that has conmpleted successfully.

    """
    # print(
    #     f"Task {sender}, ############################### succeeded with result: {result}, {sender.request}"
    # )

    # send out that task is finished without awaiting response
    fire_and_forget(sender.request.id)