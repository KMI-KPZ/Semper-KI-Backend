"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Verification handlers
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
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient, checkIfUserIsLoggedIn

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.serializer import ExceptionSerializer

from ....logics.verificationLogic import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
####################################################################################

#######################################################
class SResVerification(serializers.Serializer):
    organizationID = serializers.CharField(max_length=512)
    printerID = serializers.CharField(max_length=512)
    materialID = serializers.CharField(max_length=512)
    status = serializers.IntegerField()
    details = serializers.DictField(allow_empty=True)
    createdWhen = serializers.CharField(max_length=512)
    updatedWhen = serializers.CharField(max_length=512)
    accessedWhen = serializers.CharField(max_length=512)

#######################################################
@extend_schema(
    summary="Get the current verification for the organization",
    description=" ",
    tags=['FE - Verification'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResVerification(), allow_empty=True),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getVerificationForOrganization(request:Request):
    """
    Get the current verification for the organization",

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response
    :rtype: JSON Response

    """
    try:
        result, statusCode = getVerificationForOrganizationLogic(request)
        if isinstance(result, Exception):
            return Response({"message": str(result)}, status=statusCode)
        
        serializer = SResVerification(data=result, many=True)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (Exception) as error:
        message = f"Error in {getVerificationForOrganization.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################

#######################################################
class SReqVerification(serializers.Serializer):
    printerID = serializers.CharField(max_length=512)
    materialID = serializers.CharField(max_length=512)
    status = serializers.IntegerField(required=False)
    details = serializers.DictField(allow_empty=True, required=False)

#######################################################
@extend_schema(
    summary="Create a verification for the organization",
    description=" ",
    tags=['FE - Verification'],
    request=SReqVerification,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def createVerificationForOrganization(request:Request):
    """
    Create a verification for the organization

    :param request: POST Request
    :type request: HTTP POST
    :return: Success or not
    :rtype: Response

    """
    try:
        inSerializer = SReqVerification(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {createVerificationForOrganization.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data

        result, statusCode = createVerificationForOrganizationLogic(request, validatedInput)
        if isinstance(result, Exception):
            return Response(str(result), status=statusCode)
        
        return Response("Success", status=status.HTTP_200_OK)
        
    except (Exception) as error:
        message = f"Error in {createVerificationForOrganization.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################

#######################################################

@extend_schema(
    summary="Update a verification for the organization",
    description=" ",
    tags=['FE - Verification'],
    request=SReqVerification,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"])
@api_view(["PATCH"])
@checkVersion(0.3)
def updateVerificationForOrganization(request:Request):
    """
    Update a verification for the organization

    :param request: PATCH Request
    :type request: HTTP PATCH
    :return: Success or not
    :rtype: Response

    """
    try:
        inSerializer = SReqVerification(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {updateVerificationForOrganization.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data

        result, statusCode = updateVerificationForOrganizationLogic(request, validatedInput)
        if isinstance(result, Exception):
            return Response(str(result), status=statusCode)
        
        return Response("Success", status=status.HTTP_200_OK)
        
    except (Exception) as error:
        message = f"Error in {updateVerificationForOrganization.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################

#######################################################
@extend_schema(
    summary="Delete a verification for the organization",
    description=" ",
    tags=['FE - Verification'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["DELETE"])
@api_view(["DELETE"])
@checkVersion(0.3)
def deleteVerificationForOrganization(request:Request, printerID:str, materialID:str):
    """
    Delete a verification for the organization

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param printerID: HashID of the printer
    :type printerID: str
    :param materialID: HashID of the material
    :type materialID: str
    :return: Success or not
    :rtype: Response

    """
    try:
        result, statusCode = deleteVerificationForOrganizationLogic(request, printerID, materialID)
        if isinstance(result, Exception):
            return Response(str(result), status=statusCode)
        
        return Response("Success", status=status.HTTP_200_OK)
        
    except (Exception) as error:
        message = f"Error in {deleteVerificationForOrganization.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)