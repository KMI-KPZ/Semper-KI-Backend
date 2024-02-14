"""
Part of Semper-KI software

Akshay NS 2023

Contains: Configuration for Celery worker

"""
############################################
from __future__ import absolute_import

from dotenv import load_dotenv

from celery import Celery

import os
############################################

load_dotenv('./MSQ/.env')

broker_url = os.getenv('CELERY_BROKER_URL')
backend_url = os.getenv('CELERY_BACKEND_URL')

app = Celery('module',
             broker=broker_url,
             backend=backend_url,
             )

if __name__ == '__main__':
    app.start()