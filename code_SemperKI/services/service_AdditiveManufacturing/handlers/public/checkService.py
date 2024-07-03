"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers using simulation to check the processes
"""

import json, logging, copy, requests, random
from io import BytesIO
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
from drf_spectacular.utils import OpenApiParameter, OpenApiSchemaBase

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn
from Generic_Backend.code_General.connections import redis
from Generic_Backend.code_General.definitions import FileObjectContent

from code_SemperKI.definitions import *
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.handlers.public.files import getFileReadableStream
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.handlers.public.process import updateProcessFunction

from ...definitions import ServiceDetails

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#######################################################
def getBoundaryData(readableObject, fileName:str = "ein-dateiname.stl") -> dict:
    """
    Send the model to the Chemnitz service and get the dimensions

    :param readableObject: The model to be sent to the service with a .read() method
    :type readableObject: BytesIO | EncryptionAdapter
    :param filename: The file name
    :type filename: str
    :return: data obtained by IWU service
    :rtype: Dict

    """

    result =  {"status_code": 500, "content": {"error": "Fehler"}}

    url = settings.IWS_ENDPOINT + "/properties"
    headers = {'Content-Type': 'model/stl','content-disposition' : f'filename="{fileName}"'}

    try:
        response = requests.post(url, data=readableObject, headers=headers, stream=True)
    except Exception as e:
        logger.warning(f"Error while sending model to Chemnitz service: {str(e)}")
        return {"status_code" : 500, "content": {"error": "Fehler"}}

    # Check the response
    if response.status_code == 200:
        logger.info(f"Success capturing measurements from Chemnitz service")
        result = response.json()
        result["status_code"] = 200

    return result

#######################################################
class mbbDimensionsSerializer(serializers.Serializer):
    _1= serializers.FloatField()
    _2= serializers.FloatField()
    _3= serializers.FloatField()

#######################################################
class MeasurementsSerializer(serializers.Serializer):
    volume= serializers.FloatField()
    surfaceArea= serializers.FloatField()
    mbbDimensions = mbbDimensionsSerializer()
    mbbVolume= serializers.FloatField()

#######################################################
class SResCheckModel(serializers.Serializer):
    filename = serializers.CharField()
    measurements = MeasurementsSerializer()
    status_code = serializers.IntegerField()

#######################################################
@extend_schema(
    summary="Calculate model properties like boundary and volume",
    description=" ",
    request=None,
    responses={
        200: SResCheckModel,
        401: ExceptionSerializer,
        404: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["GET"])
@api_view(["GET"])
def checkModel(request:Request, projectID:str, processID:str, fileID:str):
    """
    Calculate model properties like boundary and volume

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with dimensions and such
    :rtype: JSON Response

    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(checkModel.__name__)
        if interface == None:
            message = "Rights not sufficient in checkModel"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        process = interface.getProcessObj(projectID, processID)
        if isinstance(process, Exception):
            message = "Model not found in checkModel"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # If calculations are already there, take these, unless they are mocked
        if fileID in process.serviceDetails[ServiceDetails.calculations] and process.serviceDetails[ServiceDetails.calculations][fileID]["measurements"]["volume"] != -1.0:
            outputSerializer = SResCheckModel(data=process.serviceDetails[ServiceDetails.calculations][fileID])
            if outputSerializer.is_valid():
                return Response(outputSerializer.data, status=status.HTTP_200_OK)
            else:
                raise Exception("Validation failed")

        model = process.serviceDetails[ServiceDetails.models][fileID]
        modelName = model[FileObjectContent.fileName]
        mock = {
            "filename": modelName,
            "measurements": {
                "volume": -1.0,
                "surfaceArea": -1.0,
                "mbbDimensions": {
                    "_1": -1.0,
                    "_2": -1.0,
                    "_3": -1.0,
                },
                "mbbVolume": -1.0,
            },
            "status_code": 200
        }

        if settings.IWS_ENDPOINT is None:
            outputSerializer = SResCheckModel(data=mock)
            if outputSerializer.is_valid():
                return Response(outputSerializer.data, status=status.HTTP_200_OK)
            else:
                raise Exception("Validation failed")

        fileContent, flag = getFileReadableStream(request, projectID, processID, model[FileObjectContent.id])
        if flag:
            resultData = getBoundaryData(fileContent, modelName)
        else:
            message = f"Error while accessing file {modelName}: {str(error)}"
            exception = str(error)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if resultData["status_code"] != 200:
            outputSerializer = SResCheckModel(data=mock)
            if outputSerializer.is_valid():
                return Response(outputSerializer.data, status=status.HTTP_200_OK)
            else:
                raise Exception("Validation failed")
        
        # save results in model file details
        changes = {"changes": {ProcessUpdates.serviceDetails: {ServiceDetails.calculations: {fileID: resultData}}}}
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False:
            message = "Rights not sufficient in checkModel while updating process"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if isinstance(message, Exception):
            raise message

        outputSerializer = SResCheckModel(data=resultData)
        if outputSerializer.is_valid():
            return Response(outputSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception("Validation failed")
    except (Exception) as error:
        message = f"Error in checkModel: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)