"""
Part of Semper-KI software

Akshay NS 2023

Contains: Init file for Celery

"""
from .celery import app as celery_app
__all__ = ('celery_app',)