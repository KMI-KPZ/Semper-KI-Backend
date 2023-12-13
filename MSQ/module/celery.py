"""
Part of Semper-KI software

Akshay NS 2023

Contains: Configuration for Celery worker

"""
from __future__ import absolute_import

from celery import Celery
############################################

app = Celery('module',
             broker='redis://redis:6379/0',
             backend='redis://redis:6379/0',
             include=['module.tasks'])

if __name__ == '__main__':
    app.start()