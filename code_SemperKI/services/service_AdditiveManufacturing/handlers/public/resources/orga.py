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
from code_SemperKI.handlers.private.knowledgeGraphDB import SReqCreateNode, SReqUpdateNode, SResGraphForFrontend, SResNode
from code_SemperKI.services.service_AdditiveManufacturing.utilities.basics import checkIfOrgaHasAMAsService
from code_SemperKI.utilities.basics import *
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph

from ....utilities import sparqlQueries
from ....service import SERVICE_NUMBER

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################


#######################################################
@extend_schema(
    summary="Returns the graph for frontend",
    description=" ",
    tags=['FE - AM Resources Organization'],
    request=None,
    responses={
        200: SResGraphForFrontend,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=False)
@checkIfOrgaHasAMAsService()
@api_view(["GET"])
@checkVersion(0.3)
def orga_getGraph(request:Request):
    """
    Returns the graph for frontend

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with graph
    :rtype: Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)

        result = pgKnowledgeGraph.getGraph(orgaID)
        if isinstance(result, Exception):
            raise result
        outDict = {"Nodes": [], "Edges": []}
        for entry in result["nodes"]:
            outEntry = {"id": entry[pgKnowledgeGraph.NodeDescription.nodeID], "name": entry[pgKnowledgeGraph.NodeDescription.nodeName]}
            outDict["Nodes"].append(outEntry)
        for entry in result["edges"]:
            outEntry = {"source": entry[0], "target": entry[1]}
            outDict["Edges"].append(outEntry)

        outSerializer = SResGraphForFrontend(data=outDict)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {orga_getGraph.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# get list of items for orga
#######################################################
class SResOrgaResources(serializers.Serializer):
    resources = serializers.ListField() # TODO specify

#######################################################
@extend_schema(
    summary="Retrieve all KG information about connected resources for an organization",
    description=" ",
    tags=['FE - AM Resources Organization'],
    request=None,
    responses={
        200: SResOrgaResources,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        404: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=False)
@checkIfOrgaHasAMAsService()
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

#######################################################
@extend_schema(
    summary="Retrieve all nodes from either the system or the orga of a certain type",
    description=" ",
    tags=['FE - AM Resources Organization'],
    request=None,
    responses={
        200: SResNode,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=False)
@checkIfOrgaHasAMAsService()
@api_view(["GET"])
@checkVersion(0.3)
def orga_getNodes(request:Request, resourceType:str):
    """
    Retrieve all nodes from either the system or the orga of a certain type

    :param request: GET Request
    :type request: HTTP GET
    :return: List of nodes
    :rtype: Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
            
        # resultsOfQueries = {"resources": []}
        # materialsRes = sparqlQueries.getAllMaterials.sendQuery()
        # for elem in materialsRes:
        #     title = elem["Material"]["value"]
        #     resultsOfQueries["materials"].append({"title": title, "URI": elem["Material"]["value"]})
        result = pgKnowledgeGraph.getNodesByType(resourceType)
        if isinstance(result, Exception):
            raise result
        # remove nodes not belonging to the system or the orga
        filteredOutput = [entry for entry in result if entry[pgKnowledgeGraph.NodeDescription.createdBy] == orgaID or entry[pgKnowledgeGraph.NodeDescription.createdBy] == pgKnowledgeGraph.defaultOwner]
                
        outSerializer = SResNode(data=filteredOutput, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {orga_getNodes.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#######################################################
@extend_schema(
    summary="Retrieve all info about a node via its ID",
    description=" ",
    tags=['FE - AM Resources Organization'],
    request=None,
    responses={
        200: SResNode,
        401: ExceptionSerializer,
        404: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=False)
@checkIfOrgaHasAMAsService()
@api_view(["GET"])
@checkVersion(0.3)
def orga_getNodeViaID(request:Request, nodeID:str):
    """
    Retrieve all info about a node via its ID

    :param request: GET Request
    :type request: HTTP GET
    :return: Json
    :rtype: Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)

        nodeInfo = pgKnowledgeGraph.getNode(nodeID)
        if isinstance(nodeInfo, Exception):
            raise nodeInfo
        if nodeInfo.createdBy != orgaID and nodeInfo.createdBy != pgKnowledgeGraph.defaultOwner:
            message = f"Rights not sufficient in {orga_getNodeViaID.cls.__name__}"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        outSerializer = SResNode(data=nodeInfo.toDict())
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {orga_getNodeViaID.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#######################################################
@extend_schema(
    summary="Gather neighboring resources of a certain type from the KG",
    description=" ",
    tags=['FE - AM Resources Organization'],
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
@checkIfOrgaHasAMAsService()
@api_view(["GET"])
@checkVersion(0.3)
def orga_getAssociatedResources(request:Request, nodeID:str, resourceType:str):
    """
    Gather neighboring resources of a certain type from the KG

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with resource of the type available
    :rtype: JSON Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)

        result = pgKnowledgeGraph.getSpecificNeighborsByType(nodeID, resourceType)
        if isinstance(result, Exception):
            raise result
        
        # remove nodes not belonging to the system or the orga
        filteredOutput = [entry for entry in result if entry[pgKnowledgeGraph.NodeDescription.createdBy] == orgaID or entry[pgKnowledgeGraph.NodeDescription.createdBy] == pgKnowledgeGraph.defaultOwner]
                
        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {orga_getAssociatedResources.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#######################################################
@extend_schema(
    summary="Gather all neighbors of a node inside an orga from the KG",
    description=" ",
    tags=['FE - AM Resources Organization'],
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
@checkIfOrgaHasAMAsService()
@api_view(["GET"])
@checkVersion(0.3)
def orga_getNeighbors(request:Request, nodeID:str):
    """
    Gather all neighbors of a node inside an orga from the KG

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with neighbors
    :rtype: JSON Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)

        result = pgKnowledgeGraph.getEdgesForNode(nodeID)
        if isinstance(result, Exception):
            raise result
        
        # remove nodes not belonging to the system or the orga
        filteredOutput = [entry for entry in result if entry[pgKnowledgeGraph.NodeDescription.createdBy] == orgaID or entry[pgKnowledgeGraph.NodeDescription.createdBy] == pgKnowledgeGraph.defaultOwner]
                
        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {orga_getNeighbors.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Creates a new node for the organization in the knowledge graph",
    description=" ",
    tags=['FE - AM Resources Organization'],
    request=SReqCreateNode,
    responses={
        200: SResNode,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
@checkIfOrgaHasAMAsService()
@api_view(["POST"])
@checkVersion(0.3)
def orga_createNode(request:Request):
    """
    Creates a new node for the organization in the knowledge graph

    :param request: POST Request
    :type request: HTTP POST
    :return: Succes or not
    :rtype: HTTP Response

    """
    try:

        serializedInput = SReqCreateNode(data=request.data)
        if not serializedInput.is_valid():
            message = f"Verification failed in {orga_createNode.cls.__name__}"
            exception = f"Verification failed {serializedInput.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = serializedInput.data

        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
        #orgaName = ProfileManagementOrganization.getOrganizationName(orgaID)
        
        # sparqlQueries.createEntryForContractor.sendQuery(
        #     {sparqlQueries.SparqlParameters.ID: orgaID, 
        #      sparqlQueries.SparqlParameters.name: orgaName,
        #      sparqlQueries.SparqlParameters.Material: materialName, 
        #      sparqlQueries.SparqlParameters.PrinterModel: printerName})
            
        # create node for the orga and link it
        resultNode = pgKnowledgeGraph.createNode(validatedInput, orgaID)
        if isinstance(resultNode, Exception):
            raise resultNode
        result = pgKnowledgeGraph.createEdge(orgaID, resultNode.nodeID) 
        if isinstance(result, Exception):
            raise result
        
        outSerializer = SResNode(data=resultNode.toDict())
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {orga_createNode.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################
@extend_schema(
    summary="Updates a node from the organization in the knowledge graph",
    description=" ",
    tags=['FE - AM Resources Organization'],
    request=SReqUpdateNode,
    responses={
        200: None,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"])
@checkIfRightsAreSufficient(json=False)
@checkIfOrgaHasAMAsService()
@api_view(["PATCH"])
@checkVersion(0.3)
def orga_updateNode(request:Request):
    """
    Updates a new node for the organization in the knowledge graph

    :param request: POST Request
    :type request: HTTP POST
    :return: Succes or not
    :rtype: HTTP Response

    """
    try:

        serializedInput = SReqUpdateNode(data=request.data)
        if not serializedInput.is_valid():
            message = f"Verification failed in {orga_updateNode.cls.__name__}"
            exception = f"Verification failed {serializedInput.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = serializedInput.data

        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
        #orgaName = ProfileManagementOrganization.getOrganizationName(orgaID)

        
        # sparqlQueries.createEntryForContractor.sendQuery(
        #     {sparqlQueries.SparqlParameters.ID: orgaID, 
        #      sparqlQueries.SparqlParameters.name: orgaName,
        #      sparqlQueries.SparqlParameters.Material: materialName, 
        #      sparqlQueries.SparqlParameters.PrinterModel: printerName})
        
        # check if the node is even associated with the organization
        result = pgKnowledgeGraph.getNode(validatedInput["nodeID"])
        if isinstance(result, Exception):
            raise result
        if result.createdBy != orgaID:
            message = f"Rights not sufficient in {orga_updateNode.cls.__name__}"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # update node for the orga
        result = pgKnowledgeGraph.updateNode(validatedInput["nodeID"], validatedInput)
        if isinstance(result, Exception):
            raise result
        
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {orga_updateNode.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################
@extend_schema(
    summary="Deletes a node from the graph by ID",
    description=" ",
    tags=['FE - AM Resources Organization'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=False)
@checkIfOrgaHasAMAsService()
@require_http_methods(["DELETE"])
@api_view(["DELETE"])
@checkVersion(0.3)
def orga_deleteNode(request:Request, nodeID:str):
    """
    Deletes a node from the graph by ID

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param nodeID: The id of the node
    :type nodeID: str
    :return: Success or not
    :rtype: Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
        #orgaName = ProfileManagementOrganization.getOrganizationName(orgaID)
        
        # sparqlQueries.createEntryForContractor.sendQuery(
        #     {sparqlQueries.SparqlParameters.ID: orgaID, 
        #      sparqlQueries.SparqlParameters.name: orgaName,
        #      sparqlQueries.SparqlParameters.Material: materialName, 
        #      sparqlQueries.SparqlParameters.PrinterModel: printerName})
        
        # check if the node is even associated with the organization
        result = pgKnowledgeGraph.getNode(nodeID)
        if isinstance(result, Exception):
            raise result
        if result.createdBy != orgaID:
            message = f"Rights not sufficient in {orga_deleteNode.cls.__name__}"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        result = pgKnowledgeGraph.deleteNode(nodeID)
        if isinstance(result, Exception):
            raise result
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {orga_deleteNode.cls.__name__}: {str(error)}"
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
    tags=['FE - AM Resources Organization'],
    request=SReqOrgaAddEdges,
    responses={
        200: None,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
@checkIfOrgaHasAMAsService()
@api_view(["POST"])
@checkVersion(0.3)
def orga_addEdgesToOrga(request:Request):
    """
    Links some things to an organization in the knowledge graph

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
        
        # sparqlQueries.createEntryForContractor.sendQuery(
        #     {sparqlQueries.SparqlParameters.ID: orgaID, 
        #      sparqlQueries.SparqlParameters.name: orgaName,
        #      sparqlQueries.SparqlParameters.Material: materialName, 
        #      sparqlQueries.SparqlParameters.PrinterModel: printerName})
            
        # link the printer to the orga
        for entry in entityIDs:
            nodeIDToBeLinked = entry
            nodeOfEntity = pgKnowledgeGraph.getNode(entry)
            # check if node belongs to SYSTEM or the orga
            if nodeOfEntity.createdBy != orgaID:
                # if it doesn't belong to the orga, create a copy for it
                newNode = pgKnowledgeGraph.copyNode(nodeOfEntity, orgaID)
                nodeIDToBeLinked = newNode.nodeID
            result = pgKnowledgeGraph.createEdge(orgaID, nodeIDToBeLinked) 
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
class SReqOrgaCreateEdge(serializers.Serializer):
    entity1ID = serializers.CharField(max_length=200)
    entity2ID = serializers.CharField(max_length=200)

#######################################################
@extend_schema(
    summary="Links two things for an organization in the knowledge graph",
    description=" ",
    tags=['FE - AM Resources Organization'],
    request=SReqOrgaCreateEdge,
    responses={
        200: None,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"])
@checkIfRightsAreSufficient(json=False)
@checkIfOrgaHasAMAsService()
@api_view(["PATCH"])
@checkVersion(0.3)
def orga_addEdgeForOrga(request:Request):
    """
    Links two things for an organization in the knowledge graph

    :param request: PATCH Request
    :type request: HTTP PATCH
    :return: Succes or not
    :rtype: HTTP Response

    """
    try:

        serializedInput = SReqOrgaCreateEdge(data=request.data)
        if not serializedInput.is_valid():
            message = f"Verification failed in {orga_addEdgeForOrga.cls.__name__}"
            exception = f"Verification failed {serializedInput.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        entity1ID = serializedInput.data["entity1ID"]
        entity2ID = serializedInput.data["entity2ID"]

        # edge already exists?
        if pgKnowledgeGraph.getIfEdgeExists(entity1ID, entity2ID):
            return Response("Success", status=status.HTTP_200_OK)

        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
        #orgaName = ProfileManagementOrganization.getOrganizationName(orgaID)

        # sparqlQueries.createEntryForContractor.sendQuery(
        #     {sparqlQueries.SparqlParameters.ID: orgaID, 
        #      sparqlQueries.SparqlParameters.name: orgaName,
        #      sparqlQueries.SparqlParameters.Material: materialName, 
        #      sparqlQueries.SparqlParameters.PrinterModel: printerName})

        result1 = pgKnowledgeGraph.getNode(entity1ID)
        if isinstance(result1, Exception):
            raise result1
        result2 = pgKnowledgeGraph.getNode(entity2ID)
        if isinstance(result2, Exception):
            raise result2
        
        node1IDToBeLinked = result1.nodeID
        # check if the node belongs to the orga
        if result1.createdBy != orgaID:
            # if it doesn't belong to the orga, create a copy for it
            newNode = pgKnowledgeGraph.copyNode(result1, orgaID)
            node1IDToBeLinked = newNode.nodeID
        
        node2IDToBeLinked = result2.nodeID
        if result2.createdBy != orgaID:
            newNode = pgKnowledgeGraph.copyNode(result2, orgaID)
            node2IDToBeLinked = newNode.nodeID
            
        # link the two things
        result = pgKnowledgeGraph.createEdge(node1IDToBeLinked, node2IDToBeLinked) 
        if isinstance(result, Exception):
            raise result
        
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {orga_addEdgeForOrga.cls.__name__}: {str(error)}"
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
    tags=['FE - AM Resources Organization'],
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
@checkIfOrgaHasAMAsService()
@api_view(["DELETE"])
@checkVersion(0.3)
def orga_removeEdgeToOrga(request:Request, entityID:str):
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

        #sparqlQueries.deletePrinterOfContractor.sendQuery(
        #    {sparqlQueries.SparqlParameters.ID: orgaID, 
        #     sparqlQueries.SparqlParameters.PrinterModel: printer})
        result = pgKnowledgeGraph.deleteEdge(orgaID, entityID)
        if isinstance(result, Exception):
            raise result
        
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {orga_removeEdgeToOrga.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Deletes the edge between two entities created by the same organization",
    description=" ",
    tags=['FE - AM Resources Organization'],
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
@checkIfOrgaHasAMAsService()
@api_view(["DELETE"])
@checkVersion(0.3)
def orga_removeEdge(request:Request, entity1ID:str, entity2ID:str):
    """
    Deletes the edge between two entities created by the same organization

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: Success or Exception
    :rtype: Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)

        result1 = pgKnowledgeGraph.getNode(entity1ID)
        if isinstance(result1, Exception):
            raise result1
        result2 = pgKnowledgeGraph.getNode(entity2ID)
        if isinstance(result2, Exception):
            raise result2
        
        if result1.createdBy != orgaID and result2.createdBy != orgaID:
            message = f"Rights not sufficient in {orga_deleteNode.cls.__name__}"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        result = pgKnowledgeGraph.deleteEdge(entity1ID,entity2ID)
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
    tags=['FE - AM Resources Organization'],
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
@checkIfOrgaHasAMAsService()
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