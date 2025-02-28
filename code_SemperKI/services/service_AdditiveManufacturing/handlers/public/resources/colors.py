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

from ....logics.colorsLogic import *

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
    :return: JSON Array with RAL table
    :rtype: JSONResponse

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
        

#######################################################
class SReqColor(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)

#######################################################
class SReqSetColor(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    processID = serializers.CharField(max_length=200)
    groupID = serializers.IntegerField()
    color = serializers.DictField()

#######################################################
@extend_schema(
    summary="Set the color",
    description=" ",
    tags=['FE - Color'],
    request=SReqSetColor,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def setColor(request:Request):
    """
    Set the color

    :param request: POST Request
    :type request: HTTP POST
    :return: Success or not
    :rtype: Response

    """
    try:
        inSerializer = SReqSetColor(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {setColor.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        result, statusCode = logicForSetColor(request, validatedInput, setColor.cls.__name__)
        if statusCode != 200:
            raise Exception(result)
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {setColor.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)