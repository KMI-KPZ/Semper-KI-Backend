To run any background/async tasks with celery,

1. import the decorator shared_task from MSQ.module.celery.
: from MSQ.module.celery import shared_task

The decorator @shared_task accepts arguments such as name of the task, eta, queue_name and other parameters.
eg.

@shared_task(name='task1', queue='highprio)
def task1(*args, **kwargs):
return 

2. Call the function (like task1) with .delay or .applyasync()

eg. task1.delay(*args, **kwargs) will push the task message onto the queue, and the celery worker running on another server will pick it up.

3. The return of task1.delay or task1.applyasync() will be an AsyncResult object containing the result, task_id, status and other parameters.

