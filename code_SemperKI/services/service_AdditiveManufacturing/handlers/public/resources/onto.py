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
from Generic_Backend.code_General.utilities.basics import checkIfRightsAreSufficient, checkIfUserIsLoggedIn, checkIfUserIsAdmin
from Generic_Backend.code_General.utilities.apiCalls import loginViaAPITokenIfAvailable
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementOrganization

from code_SemperKI.definitions import *
from code_SemperKI.handlers.private.knowledgeGraphDB import SReqCreateNode, SReqUpdateNode, SResGraphForFrontend, SResNode, SResProperties
from code_SemperKI.utilities.basics import *
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.utilities.locales import manageTranslations

from ....utilities import sparqlQueries
from ....definitions import *
from ....logics.ontoLogics import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################


#######################################################
@extend_schema(
    summary="Returns the graph for frontend",
    description=" ",
    tags=['FE - AM Resources Ontology'],
    request=None,
    responses={
        200: SResGraphForFrontend,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def onto_getGraph(request:Request):
    """
    Returns the graph for frontend

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with graph
    :rtype: Response

    """
    try:
        result, statusCode = logicForGetGraph(request)
        if isinstance(result, Exception):
            raise result
        outSerializer = SResGraphForFrontend(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {onto_getGraph.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Gathers all available resources of a certain type from the KG",
    description=" ",
    tags=['FE - AM Resources Ontology'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResNode()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def onto_getResources(request:Request, resourceType:str):
    """
    Gathers all available resources of a certain type from the KG

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with resource of the type available
    :rtype: JSON Response

    """
    try:
        result, statusCode = logicForGetResources(request, resourceType)
        if isinstance(result, Exception):
            raise result
        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {onto_getResources.cls.__name__}: {str(error)}"
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
    tags=['FE - AM Resources Ontology'],
    request=None,
    responses={
        200: SResNode,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def onto_getNodeViaID(request:Request, nodeID:str):
    """
    Retrieve all info about a node via its ID

    :param request: GET Request
    :type request: HTTP GET
    :return: Json
    :rtype: Response

    """
    try:
        result, statusCode = logicForGetNodeViaID(request, nodeID)
        if isinstance(result, Exception):
            raise result
        outSerializer = SResNode(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {onto_getNodeViaID.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Get all nodes that share that nodes unique ID",
    description=" ",
    tags=['FE - AM Resources Ontology'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResNode()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["GET"])
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@api_view(["GET"])
@checkVersion(0.3)
def onto_getNodesByUniqueID(request:Request, nodeID:str):
    """
    Get all nodes with a certain type

    :param request: GET Request
    :type request: HTTP GET
    :param nodeType: The type of the nodes
    :type nodeType: str
    :return: list of nodes
    :rtype: Response

    """
    try:
        result, statusCode = logicForGetNodesByUniqueID(request, nodeID)
        if isinstance(result, Exception):
            raise result
        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {onto_getNodesByUniqueID.cls.__name__}: {str(error)}"
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
    tags=['FE - AM Resources Ontology'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResNode()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def onto_getAssociatedResources(request:Request, nodeID:str, resourceType:str):
    """
    Gather neighboring resources of a certain type from the KG

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with resource of the type available
    :rtype: JSON Response

    """
    try:
        # materialsRes = sparqlQueries.getAllMaterials.sendQuery()
        # for elem in materialsRes:
        #     title = elem["Material"]["value"]
        #     resultsOfQueries["materials"].append({"title": title, "URI": elem["Material"]["value"]})

        result, statusCode = logicForGetAssociatedResources(request, nodeID, resourceType)
        if isinstance(result, Exception):
            raise result
        
        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {onto_getAssociatedResources.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Gather all neighbors of a node from the KG",
    description=" ",
    tags=['FE - AM Resources Ontology'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResNode()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def onto_getNeighbors(request:Request, nodeID:str):
    """
    Gather all neighbors of a node inside an orga from the KG

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with neighbors
    :rtype: JSON Response

    """
    try:
        result, statusCode = logicForGetNeighbors(request, nodeID)
        if isinstance(result, Exception):
            raise result
        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {onto_getNeighbors.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#######################################################
@extend_schema(
    summary="Creates a node in the knowledge graph",
    description=" ",
    tags=['FE - AM Resources Ontology'],
    request=SReqCreateNode,
    responses={
        200: SResNode,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def onto_addNode(request:Request):
    """
    Creates a new node

    :param request: POST Request
    :type request: HTTP POST
    :return: The node with ID
    :rtype: Response

    """
    try:
        inSerializer = SReqCreateNode(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {onto_addNode.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        
        result, statusCode = logicForAddNode(request, validatedInput)
        if isinstance(result, Exception):
            raise result

        outSerializer = SResNode(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {onto_addNode.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#######################################################
class SReqNodeFEAdmin(serializers.Serializer):
    nodeID = serializers.CharField(max_length=200, required=False, allow_blank=True)
    nodeName = serializers.CharField(max_length=200, required=False, allow_blank=True)
    context = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    nodeType = serializers.CharField(max_length=200, required=False, allow_blank=True)
    properties = serializers.ListField(child=SResProperties(), allow_empty=True, required=False)
    createdBy = serializers.CharField(max_length=200, required=False, allow_blank=True)
    active = serializers.BooleanField(required=False)

#######################################################
class SReqEdgesFEAdmin(serializers.Serializer):
    create = serializers.ListField(child=serializers.CharField(max_length=200))
    delete = serializers.ListField(child=serializers.CharField(max_length=200))

#######################################################
class SReqCreateOrUpdateAndLinkAdmin(serializers.Serializer):
    type = serializers.CharField(max_length=200)
    node = SReqNodeFEAdmin()
    edges = SReqEdgesFEAdmin()

#######################################################
@extend_schema(
    summary="Combined access for frontend to create and update together with linking",
    description=" ",
    tags=['FE - AM Resources Organization'],
    request=SReqCreateOrUpdateAndLinkAdmin,
    responses={
        200: None,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfUserIsAdmin()
@api_view(["POST"])
@checkVersion(0.3)
def onto_createOrUpdateAndLinkNodes(request:Request):
    """
    Combined access for frontend to create and update together with linking

    :param request: POST Request
    :type request: HTTP POST
    :return: JSON
    :rtype: Response

    """
    try:
        inSerializer = SReqCreateOrUpdateAndLinkAdmin(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {onto_createOrUpdateAndLinkNodes.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        validatedInput = inSerializer.data
        
        result, statusCode = logicForCreateOrUpdateAndLinkNodes(request, validatedInput)
        if isinstance(result, Exception):
            raise result
        
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {onto_createOrUpdateAndLinkNodes.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Updates the values of a node",
    description=" ",
    tags=['FE - AM Resources Ontology'],
    request=SReqUpdateNode,
    responses={
        200: SResNode,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@require_http_methods(["PATCH"])
@api_view(["PATCH"])
@checkVersion(0.3)
def onto_updateNode(request:Request):
    """
    Updates the values of a node

    :param request: PATCH Request
    :type request: HTTP PATCH
    :return: The updated node
    :rtype: Response

    """
    try:
        inSerializer = SReqUpdateNode(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {onto_updateNode.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        
        result, statusCode = logicForUpdateNode(request, validatedInput)
        if isinstance(result, Exception):
            raise result
        
        outSerializer = SResNode(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {onto_updateNode.cls.__name__}: {str(error)}"
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
    tags=['FE - AM Resources Ontology'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@require_http_methods(["DELETE"])
@api_view(["DELETE"])
@checkVersion(0.3)
def onto_deleteNode(request:Request, nodeID:str):
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
        result, statusCode = logicForDeleteNode(request, nodeID)
        if isinstance(result, Exception):
            raise result

        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {onto_deleteNode.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
class SReqOntoCreateEdge(serializers.Serializer):
    entityIDs = serializers.ListField(child=serializers.CharField(max_length=200),min_length=2)

#######################################################
@extend_schema(
    summary="Links two things in the knowledge graph",
    description=" ",
    tags=['FE - AM Resources Ontology'],
    request=SReqOntoCreateEdge,
    responses={
        200: None,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@require_http_methods(["POST"])
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
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = serializedInput.data

        result, statusCode = logicForAddEdge(request, validatedInput)
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
        

#######################################################
@extend_schema(
    summary="Remove the connection of two entities",
    description=" ",
    tags=['FE - AM Resources Ontology'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@checkIfUserIsLoggedIn()
@checkIfUserIsAdmin()
@require_http_methods(["DELETE"])
@api_view(["DELETE"])
@checkVersion(0.3)
def onto_removeEdge(request:Request, entity1ID:str, entity2ID:str):
    """
    Remove the connection of two entities

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param entity1ID: The ID of the first thing
    :type entity1ID: str
    :param entity2ID: The ID of the second thing
    :type entity2ID: str
    :return: Success or not
    :rtype: HTTP Response

    """
    try:
        result, statusCode = logicForDeleteEdge(request, entity1ID, entity2ID)
        if isinstance(result, Exception):
            raise result

        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {onto_removeEdge.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        