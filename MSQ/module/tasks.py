"""
Part of Semper-KI software

Akshay NS 2023

Contains: All the task definitions that are supposed to be run as background tasks by celery workers.

"""
from __future__ import absolute_import

from .celery import app

from celery.signals import task_success


import time

####################################################################################
@app.task(name='trialtask')
def dummy_task(x, y):
    time.sleep(10)
    # logger.info('Executing dummy_task')  # runs on the celery worker
    result = x+y
    task_id = dummy_task.request.id  # Extract task ID from request
    return result, task_id

@task_success.connect(sender=dummy_task)
def task_success_handler(sender=None, result=None, **kwargs):
    task_id = result[1] if isinstance(result, tuple) and len(result) > 1 else None
    success_message = f"Task with (ID: {task_id}) has succeeded. Result: {result}"

    # Store task ID and result in a text file
    with open('successful_tasks.txt', 'a') as file:
        file.write(success_message + '\n')

    print(success_message)
    # if kwargs.json == 'SUCCESS':
    #      taskid = kwargs.get('task-id')
    #      print(f"Task {sender.name} (ID: {taskid}) has succeeded.")
    # else:
    #     print(f"Task {sender.name} (ID: {taskid}) has failed.")


      


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