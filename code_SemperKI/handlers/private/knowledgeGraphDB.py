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

import requests
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
from code_SemperKI.modelFiles.nodesModel import NodeDescription
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#######################################################
class SResProperties(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    value = serializers.CharField(max_length=200, allow_blank=True)
    type = serializers.CharField(max_length=200)

#######################################################
class SResNode(serializers.Serializer):
    nodeID = serializers.CharField(max_length=513)
    uniqueID = serializers.CharField(max_length=513, allow_blank=True)
    nodeName = serializers.CharField(max_length=200)
    nodeType = serializers.CharField(max_length=200)
    context = serializers.CharField(max_length=10000, allow_blank=True)
    properties = serializers.ListField(child=SResProperties(), allow_empty=True)
    createdBy = serializers.CharField(max_length=513, required=False, allow_blank=True)
    clonedFrom = serializers.CharField(max_length=513, allow_blank=True)
    active = serializers.BooleanField()
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

@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getNode(request:Request, nodeID:str):
    """
    Return node by id

    :param request: GET Request
    :type request: HTTP GET
    :param nodeID: The id of the node
    :type nodeID: str
    :return: 
    :rtype: Response

    """
    try:
        node = pgKnowledgeGraph.Basics.getNode(nodeID)
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

#######################################################
class SReqCreateNode(serializers.Serializer):
    nodeName = serializers.CharField(max_length=200)
    nodeType = serializers.CharField(max_length=200, default="organization|printer|material|additionalRequirement|color")
    context = serializers.CharField(max_length=10000)
    properties = serializers.ListField(child=SResProperties(), allow_empty=True)

#######################################################
@extend_schema(
    summary="Creates a new node",
    description=" ",
    tags=['BE - Graph'],
    request=SReqCreateNode,
    responses={
        200: SResNode,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def createNode(request:Request):
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
            message = f"Verification failed in {createNode.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        result = pgKnowledgeGraph.Basics.createNode(validatedInput)
        if isinstance(result, Exception):
            raise result
        outSerializer = SResNode(data=result.toDict())
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {createNode.cls.__name__}: {str(error)}"
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
    tags=['BE - Graph'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["DELETE"])
@api_view(["DELETE"])
@checkVersion(0.3)
def deleteNode(request:Request, nodeID:str):
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
        result = pgKnowledgeGraph.Basics.deleteNode(nodeID)
        if isinstance(result, Exception):
            raise result
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {deleteNode.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################
class SReqUpdateNode(serializers.Serializer):
    nodeID = serializers.CharField(max_length=200, required=True)
    nodeName = serializers.CharField(max_length=200, required=False)
    nodeType = serializers.CharField(max_length=200, required=False)
    context = serializers.CharField(max_length=10000, required=False)
    active = serializers.BooleanField(required=False)
    properties = serializers.ListField(child=SResProperties(), allow_empty=True, required=False)
#######################################################
@extend_schema(
    summary="Updates the values of a node",
    description=" ",
    tags=['BE - Graph'],
    request=SReqUpdateNode,
    responses={
        200: SResNode,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["PATCH"])
@api_view(["PATCH"])
@checkVersion(0.3)
def updateNode(request:Request):
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
            message = f"Verification failed in {updateNode.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        result = pgKnowledgeGraph.Basics.updateNode(validatedInput["nodeID"], validatedInput)
        if isinstance(result, Exception):
            raise result
        
        outSerializer = SResNode(data=result.toDict())
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {updateNode.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################
@extend_schema(
    summary="Get all nodes with a certain type",
    description=" ",
    tags=['BE - Graph'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResNode()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getNodesByType(request:Request, nodeType:str):
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
        result = pgKnowledgeGraph.Basics.getNodesByType(nodeType)
        if isinstance(result, Exception):
            raise result

        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getNodesByType.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################
@extend_schema(
    summary="Get all nodes with a certain property",
    description=" ",
    tags=['BE - Graph'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResNode()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getNodesByProperty(request:Request, property:str):
    """
    Get all nodes with a certain property

    :param request: GET Request
    :type request: HTTP GET
    :param property: The property of the nodes
    :type property: str
    :return: list of nodes
    :rtype: Response

    """
    try:
        result = pgKnowledgeGraph.Basics.getNodesByProperty(property)
        if isinstance(result, Exception):
            raise result

        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getNodesByProperty.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Get all nodes with a certain property",
    description=" ",
    tags=['BE - Graph'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResNode()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getNodesByTypeAndProperty(request:Request, nodeType:str, nodeProperty:str, value:str):
    """
    Get all nodes with a certain property

    :param request: GET Request
    :type request: HTTP GET
    :param nodeType: The type of the node
    :type nodeType: str
    :param value: The value of the property
    :type value: str
    :param nodeProperty: The property of the node
    :type nodeProperty: str
    :return: list of nodes
    :rtype: Response

    """
    try:
        result = pgKnowledgeGraph.Basics.getNodesByTypeAndProperty(nodeType, nodeProperty, value)
        if isinstance(result, Exception):
            raise result

        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getNodesByProperty.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Return all edges belonging to a node",
    description=" ",
    tags=['BE - Graph'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResNode()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getEdgesForNode(request:Request, nodeID:str):
    """
    Return all edges belonging to a node

    :param request: GET Request
    :type request: HTTP GET
    :param nodeID: The id of the node
    :type nodeID: str
    :return: List of nodes
    :rtype: Response

    """
    try:
        result = pgKnowledgeGraph.Basics.getEdgesForNode(nodeID)
        if isinstance(result,Exception):
            raise result
        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getEdgesForNode.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Retrieve all neighbors of a node with a specific type",
    description=" ",
    tags=['BE - Graph'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResNode()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getSpecificNeighborsByType(request:Request, nodeID:str, nodeType:str):
    """
    Retrieve all neighbors of a node with a specific type

    :param request: GET Request
    :type request: HTTP GET
    :param nodeID: The id of the node
    :type nodeID: str
    :param nodeType: The type of the neighbors of interest
    :type nodeType: str
    :return: List of nodes with the specified type
    :rtype: Response

    """
    try:
        result = pgKnowledgeGraph.Basics.getSpecificNeighborsByType(nodeID, nodeType)
        if isinstance(result, Exception):
            raise result
        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getSpecificNeighborsByType.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Retrieve all neighbors of a node with a specific property",
    description=" ",
    tags=['BE - Graph'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResNode()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getSpecificNeighborsByProperty(request:Request, nodeID:str, property:str):
    """
    Retrieve all neighbors of a node with a specific property

    :param request: GET Request
    :type request: HTTP GET
    :param nodeID: The id of the node
    :type nodeID: str
    :param property: The property of the neighbors of interest
    :type property: str
    :return: List of nodes with the specified property
    :rtype: Response

    """
    try:
        result = pgKnowledgeGraph.Basics.getSpecificNeighborsByProperty(nodeID, property)
        if isinstance(result, Exception):
            raise result
        outSerializer = SResNode(data=result, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getSpecificNeighborsByProperty.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#######################################################
class SReqTwoNodes(serializers.Serializer):
    nodeID1 = serializers.CharField(max_length=200)
    nodeID2 = serializers.CharField(max_length=200)
#######################################################
@extend_schema(
    summary="Creates an edge between two nodes",
    description=" ",
    tags=['BE - Graph'],
    request=SReqTwoNodes,
    responses={
        200: None,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def createEdge(request:Request):
    """
    Creates an edge between two nodes

    :param request: POST Request
    :type request: HTTP POST
    :return: Succes or not
    :rtype: Response

    """
    try:
        inSerializer = SReqTwoNodes(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {createEdge.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        result = pgKnowledgeGraph.Basics.createEdge(validatedInput["nodeID1"], validatedInput["nodeID2"])
        if isinstance(result, Exception):
            raise result
        return Response("Success", status=status.HTTP_200_OK)
    
    except (Exception) as error:
        message = f"Error in {createEdge.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#######################################################
@extend_schema(
    summary="Deletes an existing edge",
    description=" ",
    tags=['BE - Graph'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["DELETE"])
@api_view(["DELETE"])
@checkVersion(0.3)
def deleteEdge(request:Request, nodeID1:str, nodeID2:str):
    """
    Deletes an existing edge

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param nodeID1: The first node
    :type nodeID1: str
    :param nodeID2: The second node
    :type nodeID2: str
    :return: Success or not
    :rtype: Response

    """
    try:
        result = pgKnowledgeGraph.Basics.deleteEdge(nodeID1,nodeID2)
        if isinstance(result, Exception):
            raise result
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {deleteEdge.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
class SResGraph(serializers.Serializer):
    nodes = SResNode(many=True)
    edges = serializers.ListField(child=serializers.ListField(child=serializers.CharField(max_length=200), max_length=2, min_length=2))
#######################################################
@extend_schema(
    summary="Returns the graph",
    description=" ",
    tags=['BE - Graph'],
    request=None,
    responses={
        200: SResGraph,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getGraph(request:Request):
    """
    Returns the graph

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with graph
    :rtype: Response

    """
    try:
        result = pgKnowledgeGraph.Basics.getGraph()
        if isinstance(result, Exception):
            raise result
        outSerializer = SResGraph(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getGraph.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
class SResInitialNodes(serializers.Serializer):
    id = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)
    type = serializers.CharField(max_length=200)
#######################################################
class SResInitialEdges(serializers.Serializer):
    source = serializers.CharField(max_length=200)
    target = serializers.CharField(max_length=200)
#######################################################
class SResGraphForFrontend(serializers.Serializer):
    Nodes = serializers.ListField(child=SResInitialNodes())
    Edges = serializers.ListField(child=SResInitialEdges())
#######################################################
@extend_schema(
    summary="Returns the graph for frontend",
    description=" ",
    tags=['FE - Graph'],
    request=None,
    responses={
        200: SResGraphForFrontend,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getGraphForFrontend(request:Request):
    """
    Returns the graph for frontend

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with graph
    :rtype: Response

    """
    try:
        result = pgKnowledgeGraph.Basics.getGraph()
        if isinstance(result, Exception):
            raise result
        outDict = {"Nodes": [], "Edges": []}
        for entry in result["nodes"]:
            outEntry = {"id": entry[NodeDescription.nodeID], "name": entry[NodeDescription.nodeName], "type": entry[NodeDescription.nodeType]}
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
        message = f"Error in {getGraphForFrontend.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
class SReqCreateNodeOfGraph(serializers.Serializer):
    nodeID = serializers.CharField(max_length=200, required=False, allow_blank=True)
    nodeTempID = serializers.IntegerField()
    nodeName = serializers.CharField(max_length=200)
    nodeType = serializers.CharField(max_length=200, default="organization|printer|material|additionalRequirement|color")
    context = serializers.CharField(max_length=10000)
    active = serializers.BooleanField()
    properties = serializers.ListField(child=SResProperties(), allow_empty=True)

#######################################################
class SReqGraph(serializers.Serializer):
    node = SReqCreateNodeOfGraph()
    edges = serializers.ListField(child=SReqCreateNodeOfGraph())

#######################################################
@extend_schema(
    summary="Create a graph from json",
    description=" ",
    tags=['BE - Graph'],
    request=serializers.ListSerializer(child=SReqGraph()),
    responses={
        200: SResGraph,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def createGraph(request:Request):
    """
    Create a graph from json

    :param request: POST Request
    :type request: HTTP POST
    :return: The constructed Graph
    :rtype: Response

    """
    try:
        inSerializer = SReqGraph(data=request.data, many=True)
        if not inSerializer.is_valid():
            message = f"Verification failed in {createGraph.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        result = pgKnowledgeGraph.Basics.createGraph(validatedInput)
        if isinstance(result, Exception):
            raise result
        outSerializer = SResGraph(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {createGraph.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Loads the test graph from the file",
    description=" ",
    tags=['BE - Graph'],
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
def loadTestGraph(request:Request):
    """
    Loads the test graph from the file

    :param request: GET Request
    :type request: HTTP GET
    :return: Success or not
    :rtype: Response

    """
    try:
        testGraph = open(str(settings.BASE_DIR)+'/testGraph.json').read()
        tGAsDict = json.loads(testGraph)
        result = pgKnowledgeGraph.Basics.createGraph(tGAsDict)
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {loadTestGraph.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Deletes the whole graph",
    description=" ",
    tags=['BE - Graph'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@require_http_methods(["DELETE"])
@api_view(["DELETE"])
@checkVersion(0.3)
def deleteGraph(request:Request):
    """
    Deletes the whole graph

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: Success or not
    :rtype: Response

    """
    try:
        result = pgKnowledgeGraph.Basics.deleteGraph()
        if isinstance(result, Exception):
            raise result
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {deleteGraph.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        