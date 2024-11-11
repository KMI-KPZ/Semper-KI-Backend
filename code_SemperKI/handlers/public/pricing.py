"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Handlers showing prices and receiving parameters
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
from Generic_Backend.code_General.utilities.basics import checkIfRightsAreSufficient, checkIfUserIsLoggedIn, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.serializer import ExceptionSerializer

from ...logics.pricing import logicOfPriceCalculation

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################


#######################################################
class SReqParametersForPricing(serializers.Serializer):
    pass

#######################################################
class SResPrices(serializers.Serializer):
    pass

#######################################################
@extend_schema(
    summary="Calculate a price from the given parameters",
    description=" ",
    tags=['FE- Price'],
    request=SReqParametersForPricing,
    responses={
        200: SResPrices,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def calculatePriceForContractor(request:Request):
    """
    Calculate a price from the given parameters

    :param request: POST Request
    :type request: HTTP POST
    :return: JSON
    :rtype: JSONResponse

    """
    try:
        inSerializer = SReqParametersForPricing(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {calculatePriceForContractor.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data

        # TODO
        logicOfPriceCalculation()

        output = {}

        outSerializer = SResPrices(data=output)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {calculatePriceForContractor.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)