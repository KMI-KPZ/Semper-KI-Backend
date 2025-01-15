"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers using simulation to check the processes
"""

import logging
from django.views.decorators.http import require_http_methods

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema


from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkVersion


from code_SemperKI.definitions import *
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.postgresql import pgProcesses

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

