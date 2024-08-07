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

# get list of items for orga
#######################################################
class SResOrgaResources(serializers.Serializer):
    resources = serializers.ListField() # TODO specify

#######################################################
@extend_schema(
    summary="Retrieve all KG information about connected resources for an organization",
    description=" ",
    tags=['FE - AM Resources'],
    request=None,
    responses={
        200: SResOrgaResources,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
@checkVersion(0.3)
def orga_getResources(request:Request):
    """
    Retrieve all KG information about connected resources for an organization

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with list of resources
    :rtype: JSON Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)

        #Check that this orga provides AM as service
        if SERVICE_NUMBER not in ProfileManagementOrganization.getSupportedServices(orgaID):
            message = f"Orga does not offer service in {orga_getResources.cls.__name__}"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        outDict = {"resources": []}
        #result = sparqlQueries.getServiceProviders.sendQuery({sparqlQueries.SparqlParameters.ID: orgaID})
        # TODO: Parse and serialize output
        result = pgKnowledgeGraph.getEdgesForNode(orgaID)
        if isinstance(result, Exception):
            raise result
        outDict["resources"].extend(result)
        
        outSerializer = SResOrgaResources(data=outDict)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {orga_getResources.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# set printer/material for orga (keep in mind: one item at the time for sparql)
#######################################################
class SReqOrgaAddEdges(serializers.Serializer):
    entityIDs = serializers.ListField(child=serializers.CharField(max_length=200))

#######################################################
@extend_schema(
    summary="Links some things to an organization in the knowledge graph",
    description=" ",
    tags=['FE - AM Resources'],
    request=SReqOrgaAddEdges,
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
def orga_addEdgesToOrga(request:Request):
    """
    Edges some things to an organization in the knowledge graph

    :param request: POST Request
    :type request: HTTP POST
    :return: Succes or not
    :rtype: HTTP Response

    """
    try:

        serializedInput = SReqOrgaAddEdges(data=request.data)
        if not serializedInput.is_valid():
            message = f"Verification failed in {orga_addEdgesToOrga.cls.__name__}"
            exception = f"Verification failed {serializedInput.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        entityIDs = serializedInput.data["entityIDs"]

        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
        #orgaName = ProfileManagementOrganization.getOrganizationName(orgaID)

        #Check that this orga provides AM as service
        if SERVICE_NUMBER not in ProfileManagementOrganization.getSupportedServices(orgaID):
            message = f"Orga does not offer service in {orga_addEdgesToOrga.cls.__name__}"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # sparqlQueries.createEntryForContractor.sendQuery(
        #     {sparqlQueries.SparqlParameters.ID: orgaID, 
        #      sparqlQueries.SparqlParameters.name: orgaName,
        #      sparqlQueries.SparqlParameters.Material: materialName, 
        #      sparqlQueries.SparqlParameters.PrinterModel: printerName})
            
        # link the printer to the orga
        for entry in entityIDs:
            result = pgKnowledgeGraph.createEdge(orgaID, entry) 
            if isinstance(result, Exception):
                raise result
        
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {orga_addEdgesToOrga.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Remove the connection of an organization to something",
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
@require_http_methods(["DELETE"])
@checkIfRightsAreSufficient(json=False)
@api_view(["DELETE"])
@checkVersion(0.3)
def orga_removeEdge(request:Request, entityID:str):
    """
    Remove the connection of an organization to something

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param entityID: The ID of the thing removed as an edge to that orga
    :type entityID: str
    :return: Success or not
    :rtype: HTTP Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)

        #Check that this orga provides AM as service
        if SERVICE_NUMBER not in ProfileManagementOrganization.getSupportedServices(orgaID):
            message = f"Orga does not offer service in {orga_removeEdge.cls.__name__}"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        #sparqlQueries.deletePrinterOfContractor.sendQuery(
        #    {sparqlQueries.SparqlParameters.ID: orgaID, 
        #     sparqlQueries.SparqlParameters.PrinterModel: printer})
        result = pgKnowledgeGraph.deleteEdge(orgaID, entityID)
        if isinstance(result, Exception):
            raise result
        
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {orga_removeEdge.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

#######################################################
@extend_schema(
    summary="Remove all connections of an organization",
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
@require_http_methods(["DELETE"])
@checkIfRightsAreSufficient(json=False)
@api_view(["DELETE"])
@checkVersion(0.3)
def orga_removeAll(request:Request):
    """
    Remove all connections of an organization

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: Success or not
    :rtype: HTTP Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)

        #Check that this orga provides AM as service
        if SERVICE_NUMBER not in ProfileManagementOrganization.getSupportedServices(orgaID):
            message = f"Orga does not offer service in {orga_removeAll.cls.__name__}"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # sparqlQueries.deleteAllFromContractor.sendQuery(
        #     {sparqlQueries.SparqlParameters.ID: orgaID})
        result = pgKnowledgeGraph.getEdgesForNode(orgaID)
        if isinstance(result, Exception):
            raise result
        for entry in result:
            retVal = pgKnowledgeGraph.deleteEdge(orgaID, entry[pgKnowledgeGraph.NodeDescription.nodeID])
            if isinstance(retVal, Exception):
                raise retVal
        
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {orga_removeAll.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)