"""
Part of Semper-KI software

Akshay NS 2023

Contains: All the task definitions that are supposed to be run as background tasks by celery workers.

"""
from __future__ import absolute_import

from .celery import app

from celery.signals import task_prerun, task_postrun

import time

####################################################################################
@app.task(name='trialtask')
def dummy_task(x, y):
    time.sleep(30)
    # logger.info('Executing dummy_task')  # runs on the celery worker
    result = x+y
    # logger.info('Finished dummy_task')  # runs on the celery worker
    return (result,'The celery task is working!')  # will be returned to the backend

@task_prerun.connect(sender=dummy_task)
def task_prerun_notifier(sender=None, **kwargs):
    print("From task_prerun_notifier =======================================================> Running just before dummy_task() executes")

@task_postrun.connect(sender=dummy_task)
def task_postrun_notifier(sender=None, **kwargs):

    print("From task_postrun_notifier ======================================================> OK DONE!")    


####################################################################################

@app.task(name='calculateprice')
def calculatePrice_Mock(items):
    """
    Random prices calculation
    """
    summedUpPrices= 0
    priceForEach = []
    for idx, elem in enumerate(items):
        price = random.randint(1,100)
        summedUpPrices += price
        priceForEach.append(price)
    
    return summedUpPrices, priceForEach

####################################################################################