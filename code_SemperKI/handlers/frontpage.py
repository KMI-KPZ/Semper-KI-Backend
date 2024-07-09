"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Views for some backend websites
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from logging import getLogger

from ..definitions import SEMPER_KI_VERSION

logger = getLogger("django")


#######################################################
