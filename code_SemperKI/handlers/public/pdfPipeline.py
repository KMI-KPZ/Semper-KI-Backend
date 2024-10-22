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

from llama_parse import LlamaParse

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.apiCalls import loginViaAPITokenIfAvailable
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.utilities.responseFormatsForPDFExtraction import PrinterResponse, MaterialResponse

from code_SemperKI.connections.openai import callChatInterface

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
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        category = validatedInput["category"]
        if category not in ['printer', 'material']:
            raise Exception("Invalid category selected!")
        
        if "gptModel" in validatedInput:
            gptModel = validatedInput["gptModel"]
        else:
            gptModel = "gpt-4o-mini"
        
        # gather uploaded file(s)
        listOfJSONs = []
        fileNames = list(request.FILES.keys())
        for fileName in fileNames:
            for file in request.FILES.getlist(fileName):
                # send to extraction pipeline

                # read file and extract text
                fileInBytes = BytesIO(file.read())
                documents = LlamaParse(api_key=settings.LLAMA_CLOUD_API_KEY, result_type="text").load_data(fileInBytes, extra_info={"file_name": fileName})
                if documents:
                    textContent = "\n\n".join([doc.text for doc in documents])
                else:
                    raise Exception("No content extracted from the provided PDF content.")
                
                if textContent is None:
                    raise Exception("No text extracted from the PDF. Exiting.")

                # Convert text to JSON
                if category == 'printer':
                    jsonData = callChatInterface(gptModel, textContent, "You are a helpful assistant and expert in additive manufacturing. Categorize & extract 3D printer specifications key info from a factsheet:", PrinterResponse)
                elif category == 'material':
                    jsonData = callChatInterface(gptModel, textContent, "You are a helpful assistant and expert in additive manufacturing. Categorize & extract AM material specifications key info from a factsheet:", MaterialResponse)
                if isinstance(jsonData, Exception):
                    raise jsonData
                listOfJSONs.append(jsonData)

        # put out through serializer
        outSerializer = serializers.ListSerializer(child=serializers.DictField(), data=listOfJSONs)
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