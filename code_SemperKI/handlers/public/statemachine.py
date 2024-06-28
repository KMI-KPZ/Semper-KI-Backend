"""
Part of Semper-KI software

Akshay NS 2024

Contains: 
"""

import json, logging, copy
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.states.states import processStatusAsInt, ProcessStatusAsString, StateMachine

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#########Serializer#############
#TODO Add serializer  
# "getStateMachine": ("public/getStateMachine/", statemachine.getStateMachine),
#######################################################
@extend_schema(
    summary="Print out the whole state machine and all transitions",
    description=" ",
    request=None,
    tags = ['state machine'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
# @checkIfUserIsLoggedIn()
# @require_http_methods(["GET"])
# @checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
def getStateMachine(request):
    """
    Print out the whole state machine and all transitions

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with graph in JSON Format
    :rtype: JSONResponse
    
    """
    try:
        sm = StateMachine(initialAsInt=0)
        paths = sm.showPaths()
        assert isinstance(paths, dict), f"In {getStateMachine.__name__}: expected paths to be of type dict instead got {type(paths)}"
        return Response(paths, status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in getStateMachine: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)