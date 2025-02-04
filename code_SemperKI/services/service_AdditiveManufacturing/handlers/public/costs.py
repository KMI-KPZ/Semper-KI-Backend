"""
Part of Semper-KI software

Silvio Weging 2025

Contains: API endpoint for cost-calculations
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
from code_SemperKI.utilities.serializer import ExceptionSerializer

from ...logics.costsLogic import logicForCosts

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
#######################################################
class SReqCostsAddManValues(serializers.Serializer):
    key = serializers.CharField(max_length=200)
    value = serializers.FloatField()
    unit = serializers.CharField(max_length=200)

# #######################################################
# class SReqAddManValues(serializers.Serializer):
#     powerCosts = serializers.FloatField()
#     margin = serializers.FloatField()
#     personnelCosts = serializers.FloatField()
#     costRatePersonnelEngineering = serializers.FloatField()
#     repairCosts = serializers.FloatField()
#     additionalFixedCosts = serializers.FloatField()
#     costRateEquipmentEngineering = serializers.FloatField()
#     fixedCostsEquipmentEngineering = serializers.FloatField()
#     safetyGasCosts = serializers.FloatField()
#     roomCosts = serializers.FloatField()
#######################################################
class SReqCostsAdditiveManufacturing(serializers.Serializer):
    ADDITIVE_MANUFACTURING = serializers.ListField(child=SReqCostsAddManValues())
#######################################################
class SReqCostsServices(serializers.Serializer):
    services = SReqCostsAdditiveManufacturing()
#######################################################
class SReqCostsOrgaDetails(serializers.Serializer):
    details = SReqCostsServices()

#######################################################
class SReqCostsMaterial(serializers.Serializer):
    density = serializers.FloatField()
    printingSpeed = serializers.FloatField()
    acquisitionCosts = serializers.FloatField()

#######################################################
class SReqCostsPostProcessings(serializers.Serializer):
    fixedCostsPostProcessing = serializers.FloatField()
    treatmentCostsPostProcessing = serializers.FloatField()

#######################################################
class SReqCostsModels(serializers.Serializer):
    levelOfDetail = serializers.FloatField()
    isFile = serializers.FloatField()
    quantity = serializers.FloatField()
    complexity = serializers.FloatField()
    height = serializers.FloatField()
    length = serializers.FloatField()
    width = serializers.FloatField()
    volume = serializers.FloatField()
    id = serializers.CharField(max_length=200)

#######################################################
class SReqCostsGroups(serializers.Serializer):
    material = SReqCostsMaterial()
    postProcessings = serializers.DictField(child=SReqCostsPostProcessings())
    models = serializers.DictField(child=SReqCostsModels())

#######################################################
class SReqCostsPrinterProperties(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    value = serializers.CharField(max_length=200)
# #######################################################
# class SReqCostsProperties(serializers.Serializer):
#     costRatePersonalMachine = serializers.FloatField()
#     buildChamberHeight = serializers.FloatField()
#     buildChamberLength = serializers.FloatField()
#     buildChamberWidth = serializers.FloatField()
#     machineMaterialLoss = serializers.FloatField()
#     machineBatchDistance = serializers.FloatField()
#     layerThickness = serializers.CharField(max_length=200)
#     machineSurfaceArea = serializers.FloatField()
#     machineSetUpSimple = serializers.FloatField()
#     machineSetUpComplex = serializers.FloatField()
#     averagePowerConsumption = serializers.FloatField()
#     machineHourlyRate = serializers.FloatField()
#     coatingTime = serializers.FloatField()
#     buildRate = serializers.FloatField()
#     fillRate = serializers.FloatField()
#     nozzleDiameter = serializers.FloatField()
#     maxPrintingSpeed = serializers.FloatField()

#######################################################
class SReqCostsPrinters(serializers.Serializer):
    technology = serializers.CharField(max_length=200)
    properties = serializers.ListField(child=SReqCostsPrinterProperties())

#######################################################
class SReqCosts(serializers.Serializer):
    organization = SReqCostsOrgaDetails()
    groups = serializers.ListField(child=SReqCostsGroups())
    printers = serializers.ListField(child=SReqCostsPrinters())

#######################################################
@extend_schema(
    summary="Calculate costs",
    description=" ",
    tags=['BE - Costs'],
    request=SReqCosts,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def apiCalculateCosts(request:Request):
    """
    Calculate costs

    :param request: POST Request
    :type request: HTTP POST
    :return: 
    :rtype: Response

    """
    try:
        inSerializer = SReqCosts(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {apiCalculateCosts.cls.__name__} {inSerializer.errors}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        outDict, statusCode = logicForCosts(validatedInput)
        if isinstance(outDict, Exception):
            raise outDict
        return Response(outDict, status=statusCode)

    except (Exception) as error:
        message = f"Error in {apiCalculateCosts.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)