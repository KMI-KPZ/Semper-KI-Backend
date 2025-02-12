"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Handler for color specific requests
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
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.serializer import ExceptionSerializer

from ....logics.colorsLogic import logicForGetRALList

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#######################################################
class SResRALListEntry(serializers.Serializer):
    RAL = serializers.CharField(max_length=200)
    RALName = serializers.CharField(max_length=200)
    Hex = serializers.CharField(max_length=200)

#######################################################
@extend_schema(
    summary="Get the RAL table and convert to frontend format",
    description=" ",
    tags=['FE - Colors'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResRALListEntry()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getRALList(request:Request):
    """
    Get the RAL table and convert to frontend format
    
    :param request: GET Request
    :type request: HTTP GET
    :return: 
    :rtype: Response

    """
    try:
        ralList = logicForGetRALList(request)
        outSerializer = serializers.ListSerializer(child=SResRALListEntry(), data=ralList)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getRALList.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)