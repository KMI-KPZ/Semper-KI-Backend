"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Handlers for handling the database backed knowledge graph
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
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#######################################################
class SResNode(serializers.Serializer):
    nodeID = serializers.CharField(max_length=513)
    nodeName = serializers.CharField(max_length=200)
    nodeType = serializers.CharField(max_length=200)
    context = serializers.CharField(max_length=10000)
    properties = serializers.DictField()
    createdWhen = serializers.CharField(max_length=200)
    updatedWhen = serializers.CharField(max_length=200)
    accessedWhen = serializers.CharField(max_length=200)

#######################################################
@extend_schema(
    summary="Return node by id",
    description=" ",
    tags=['BE - Graph'],
    request=None,
    responses={
        200: SResNode,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getNode(request:Request, nodeID:str):
    """
    Return node by id

    :param request: GET Request
    :type request: HTTP GET
    :return: 
    :rtype: Response

    """
    try:
        node = pgKnowledgeGraph.getNode(nodeID)
        if isinstance(node, Exception):
            raise node
        outSerializer = SResNode(data=node.toDict())
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getNode.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)