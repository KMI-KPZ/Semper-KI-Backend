"""
Part of Semper-KI software

Silvio Weging, Mahdi Hedayat Mahmoudi 2024

Contains: Handler for processing pdfs to json
"""

from io import BytesIO
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
from Generic_Backend.code_General.utilities.apiCalls import loginViaAPITokenIfAvailable
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient, checkIfUserIsAdmin

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.serializer import ExceptionSerializer

from ....logics.pdfPipelineLogics import logicForPDFPipeline, logicForExtractFromJSON

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#######################################################
class SReqPDFExtraction(serializers.Serializer):
    file = serializers.ListField(child=serializers.FileField())
    category = serializers.CharField(max_length=200)
    gptModel = serializers.CharField(max_length=200, required=False, allow_blank=True)

#######################################################
#class SResExtractedPDF(serializers.Serializer):
#    projectID = serializers.CharField(max_length=200)


#######################################################
@extend_schema(
    summary="upload a pdf and get back the converted json",
    description=" ",
    tags=['BE - PDF'],
    request=SReqPDFExtraction,
    responses={
        200: serializers.ListSerializer(child=serializers.DictField()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["POST"])
@loginViaAPITokenIfAvailable()
@checkIfUserIsAdmin(json=True)
@api_view(["POST"])
@checkVersion(0.3)
def extractFromPDF(request:Request):
    """
    upload a pdf and get back the converted json

    :param request: POST Request
    :type request: HTTP POST
    :return: JSON
    :rtype: JSONResponse

    """
    try:
        # serializer
        inSerializer = SReqPDFExtraction(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {extractFromPDF.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        result, statusCode = logicForPDFPipeline(validatedInput, request.FILES)
        if statusCode != 200:
            raise Exception(result)

        # put out through serializer
        outSerializer = serializers.ListSerializer(child=serializers.DictField(), data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {extractFromPDF.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  

class ReqExtractFromJSON(serializers.Serializer):
    data = serializers.ListField(child=serializers.DictField())
    category = serializers.CharField(max_length=200)  

#######################################################
@extend_schema(
    summary="upload a json and write it to the KG",
    description=" ",
    tags=['BE - PDF'],
    request=ReqExtractFromJSON,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["POST"])
@loginViaAPITokenIfAvailable()
@checkIfUserIsAdmin(json=True)
@api_view(["POST"])
@checkVersion(0.3)
def extractFromJSON(request: Request):
    """
    Take a json and write it to the KG
    
    :param request: POST Request
    :type request: HTTP POST
    :return: JSON
    :rtype: JSONResponse
    """
    try:
        # serializer
        inSerializer = ReqExtractFromJSON(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {extractFromJSON.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        result, statusCode = logicForExtractFromJSON(validatedInput)
        if statusCode != 200:
            raise Exception(result)
        return Response(status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {extractFromJSON.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)