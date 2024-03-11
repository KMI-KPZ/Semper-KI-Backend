"""
Part of Semper-KI software

Akshay NS 2024

Contains: Insert additional settings for celery worker over here.

"""

from kombu import Exchange, Queue

enable_utc = True


timezone = "Europe/Berlin"
exchange1 = Exchange("local", type="direct")

accept_content = ["json"]  # add pickle only if you need it
result_accept_content = ["json"]  # add pickle only if you need it

task_queues = (Queue("local", exchange1, routing_key="local"),)
