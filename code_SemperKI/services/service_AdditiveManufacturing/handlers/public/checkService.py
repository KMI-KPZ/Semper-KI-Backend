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

from ...logics.checkServiceLogic import logicForCheckModel


logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################



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
    tags=['FE - AM Check model'],
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
@checkVersion(0.3)
def checkModel(request:Request, projectID:str, processID:str, fileID:str):
    """
    Calculate model properties like boundary and volume

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with dimensions and such
    :rtype: JSON Response

    """
    try:
        result, statusCode = logicForCheckModel(request, checkModel.cls.__name__, projectID, processID, fileID)
        if isinstance(result, Exception):
            message = f"Error in {checkModel.cls.__name__}: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        outputSerializer = SResCheckModel(data=result)
        if outputSerializer.is_valid():
            return Response(outputSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception("Validation failed")
    except (Exception) as error:
        message = f"Error in {checkModel.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################
def checkIfSelectionIsAvailable(processObj:pgProcesses.Process|pgProcesses.ProcessInterface):
    """
    Check if the selection really is available or not.
    Currently a dummy

    :param processObj: The process in question
    :type processObj: Process or ProcessInterface
    :return: True if everything is in order, False if something is missing
    :rtype: bool
    
    """
    serviceDetails = processObj.serviceDetails
    processDetails = processObj.processDetails
    # TODO
    return True