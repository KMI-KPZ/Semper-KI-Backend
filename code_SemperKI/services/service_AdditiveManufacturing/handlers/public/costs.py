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
class SReqCostsOrgaDetails(serializers.Serializer):
    powerCosts = serializers.CharField(max_length=200, default="0.17 €/kWh")
    margin = serializers.CharField(max_length=200, default="10 %")
    personnelCosts = serializers.CharField(max_length=200, default="0 €/h")
    costRatePersonnelEngineering = serializers.CharField(max_length=200, default="35 €/h")
    repairCosts = serializers.CharField(max_length=200, default="0.025 %")
    additionalFixedCosts = serializers.CharField(max_length=200, default="0 €")
    costRateEquipmentEngineering = serializers.CharField(max_length=200, default="2 €/h")
    fixedCostsEquipmentEngineering = serializers.CharField(max_length=200, default="2 €/kWh")
    safetyGasCosts = serializers.CharField(max_length=200, default="20 €/h")
    roomCosts = serializers.CharField(max_length=200, default="14.5 €/m²")

#######################################################
class SReqCostsMaterial(serializers.Serializer):
    density = serializers.CharField(max_length=200, default="4.43 g/cm³")
    printingSpeed = serializers.CharField(max_length=200, default="60 cm/h")
    acquisitionCosts = serializers.CharField(max_length=200, default="400 €")

#######################################################
class SReqCostsPostProcessings(serializers.Serializer):
    fixedCostsPostProcessing = serializers.CharField(max_length=200, default="0 €")
    treatmentCostsPostProcessing = serializers.CharField(max_length=200, default="0 €")

#######################################################
class SReqCostsModels(serializers.Serializer):
    levelOfDetail = serializers.IntegerField(default=1)
    quantity = serializers.IntegerField(default=1)
    complexity = serializers.IntegerField(default=1)
    height = serializers.CharField(max_length=200, default="100 mm")
    length = serializers.CharField(max_length=200, default="100 mm")
    width = serializers.CharField(max_length=200, default="100 mm")
    volume = serializers.CharField(max_length=200, default="1000000 mm³")
    id = serializers.CharField(max_length=200, default="testModel_1")

#######################################################
class SReqCostsProperties(serializers.Serializer):
    costRatePersonalMachine = serializers.CharField(max_length=200, default="26 €/h")
    chamberBuildHeight = serializers.CharField(max_length=200, default="500 mm")
    chamberBuildWidth = serializers.CharField(max_length=200, default="500 mm")
    chamberBuildLength = serializers.CharField(max_length=200, default="500 mm")
    lossOfMaterial = serializers.CharField(max_length=200, default="30 %")
    machineBatchDistance = serializers.CharField(max_length=200, default="10 mm")
    possibleLayerHeights = serializers.CharField(max_length=200, default="75, 30, 15")
    machineSurfaceArea = serializers.CharField(max_length=200, default="1.8 m²")
    machineSetUpSimple = serializers.CharField(max_length=200, default="1")
    machineSetUpComplex = serializers.CharField(max_length=200, default="2")
    averagePowerConsumption = serializers.CharField(max_length=200, default="5 €/kWh")
    machineUsageCosts = serializers.CharField(max_length=200, default="51.8 €/h")
    coatingTime = serializers.CharField(max_length=200, default="9 h")
    buildRate = serializers.CharField(max_length=200, default="50 cm³/h")
    fillRate = serializers.CharField(max_length=200, default="100 %")
    nozzleDiameter = serializers.CharField(max_length=200, default="0.4 mm")
    maxPrintingSpeed = serializers.CharField(max_length=200, default="60 cm/h")

#######################################################
class SReqCostsPrinters(serializers.Serializer):
    technology = serializers.CharField(max_length=200, default="Powder Bed Fusion")
    properties = SReqCostsProperties()

#######################################################
class SReqCosts(serializers.Serializer):
    organization = SReqCostsOrgaDetails()
    material = SReqCostsMaterial()
    postProcessings = serializers.DictField(child=SReqCostsPostProcessings())#, default={"testPostProcessing_1": SReqCostsPostProcessings()})
    models = serializers.DictField(child=SReqCostsModels())#, default={"testModel_1": SReqCostsModels()})
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