"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Calls to ontology for adding and retrieving data
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
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementOrganization

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph

from ....utilities import sparqlQueries
from ....service import SERVICE_NUMBER

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

# get list of all printer/material
#######################################################
class SResMaterialList(serializers.Serializer):
    resources = serializers.ListField() #TODO specify
#######################################################
@extend_schema(
    summary="Gathers all available resources of a certain type from the KG",
    description=" ",
    tags=['FE - AM Resources'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
@checkVersion(0.3)
def onto_getResource(request:Request, resourceType:str):
    """
    Gathers all available resources of a certain type from the KG

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with resource of the type available
    :rtype: JSON Response

    """
    try:
        resultsOfQueries = {"resources": []}
        # materialsRes = sparqlQueries.getAllMaterials.sendQuery()
        # for elem in materialsRes:
        #     title = elem["Material"]["value"]
        #     resultsOfQueries["materials"].append({"title": title, "URI": elem["Material"]["value"]})
        result = pgKnowledgeGraph.getNodesByType(resourceType)
        if isinstance(result, Exception):
            raise result
        resultsOfQueries["resources"].extend(result)
        
        outSerializer = SResMaterialList(data=resultsOfQueries)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {onto_getResource.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
class SReqOntoCreateEdge(serializers.Serializer):
    ID1 = serializers.CharField(max_length=200)
    ID2 = serializers.CharField(max_length=200)

#######################################################
@extend_schema(
    summary="Links two things in the knowledge graph",
    description=" ",
    tags=['FE - AM Resources'],
    request=SReqOntoCreateEdge,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
@api_view(["POST"])
@checkVersion(0.3)
def onto_addEdge(request:Request):
    """
    Links two things in the knowledge graph

    :param request: POST Request
    :type request: HTTP POST
    :return: Succes or not
    :rtype: HTTP Response

    """
    try:

        serializedInput = SReqOntoCreateEdge(data=request.data)
        if not serializedInput.is_valid():
            message = f"Verification failed in {onto_addEdge.cls.__name__}"
            exception = f"Verification failed {serializedInput.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        ID1 = serializedInput.data["ID1"]
        ID2 = serializedInput.data["ID2"]
            
        result = pgKnowledgeGraph.createEdge(ID1, ID2) 
        if isinstance(result, Exception):
            raise result
        
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {onto_addEdge.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)