"""
Part of Semper-KI software

Silvio Weging 2024

Contains: General handlers for the AM knowledge graph
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
from code_SemperKI.handlers.private.knowledgeGraphDB import SResProperties
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.serializer import ExceptionSerializer

from ....connections.postgresql import pgKG

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#######################################################
@extend_schema(
    summary="Retrieves the definition of possible properties for a specific node type",
    description=" ",
    tags=['FE - Graph'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getPropertyDefinitionFrontend(request:Request, nodeType:str):
    """
    Retrieves the definition of possible properties for a specific node type

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON
    :rtype: Response

    """
    try:
        propertyDefinitions = pgKG.getPropertyDefinitionForNodeType(nodeType)
        outSerializer = SResProperties(data=propertyDefinitions, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getPropertyDefinitionFrontend.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)