# Initial setup for Message Queue Service (MSQ)
- A separate network (MSQ) is created which includes the celery-worker, celery-beat, flower, redis-broker and redis-insight services.
- Flower APIs are used to trigger and obtain results of asynchronous tasks.
- A tasks.py file, within the MSQ folder contains the definitions of all the tasks that are supposed to be run asynchronously/through celery workers.
 