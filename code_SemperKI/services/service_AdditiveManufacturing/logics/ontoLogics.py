"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Logic functions for service specific organization KG stuff
"""

import json, logging, copy
from datetime import datetime
from django.conf import settings

from rest_framework.request import Request

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementOrganization
from Generic_Backend.code_General.utilities.basics import checkIfRightsAreSufficient, checkIfUserIsLoggedIn, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import *
from code_SemperKI.handlers.private.knowledgeGraphDB import SReqCreateNode, SReqUpdateNode, SResGraphForFrontend, SResNode, SResProperties
from code_SemperKI.utilities.basics import *
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.utilities.locales import manageTranslations

from ..definitions import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
##################################################
def logicForGetGraph(request:Request) -> tuple[dict|Exception, int]:
    """
    Returns the graph for frontend

    """
    try:
        result = pgKnowledgeGraph.Basics.getGraph()
        if isinstance(result, Exception):
            raise result
        outDict = {"Nodes": [], "Edges": []}
        for entry in result["nodes"]:
            outEntry = {"id": entry[pgKnowledgeGraph.NodeDescription.nodeID], "name": entry[pgKnowledgeGraph.NodeDescription.nodeName], "type": entry[pgKnowledgeGraph.NodeDescription.nodeType]}
            outDict["Nodes"].append(outEntry)
        for entry in result["edges"]:
            outEntry = {"source": entry[0], "target": entry[1]}
            outDict["Edges"].append(outEntry)

        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},fetched,{Logging.Object.OBJECT},graph," + str(datetime.now()))
        return outDict, 200
    except Exception as e:
        loggerError.error("Error in logicForGetGraph: " + str(e))
        return e, 500
    
##################################################
def logicForGetResources(request:Request, resourceType:str) -> tuple[list[dict]|Exception, int]:
    """
    Gathers all available resources of a certain type from the KG

    """
    try:
        result = pgKnowledgeGraph.Basics.getNodesByType(resourceType)
        if isinstance(result, Exception):
            raise result
        
        locale = ProfileManagementOrganization.getUserLocale(request.session)
        for elemIdx, elem in enumerate(result):
            for propIdx, prop in enumerate(elem[pgKnowledgeGraph.NodeDescription.properties]):
                result[elemIdx][pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.name] = manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,prop[pgKnowledgeGraph.NodePropertyDescription.key]])

        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},fetched,{Logging.Object.OBJECT},nodes of type {resourceType}," + str(datetime.now()))
        return result, 200
    except Exception as e:
        loggerError.error("Error in logicForGetResources: " + str(e))
        return e, 500
    
##################################################
def logicForGetNodeViaID(request:Request, nodeID:str) -> tuple[dict|Exception, int]:
    """
    Retrieve all info about a node via its ID

    """
    try:
        nodeInfo = pgKnowledgeGraph.Basics.getNode(nodeID)
        if isinstance(nodeInfo, Exception):
            raise nodeInfo

        locale = ProfileManagementOrganization.getUserLocale(request.session)
        nodeDict = nodeInfo.toDict()
        for propIdx, prop in enumerate(nodeDict[pgKnowledgeGraph.NodeDescription.properties]):
            nodeDict[pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.name] = manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,prop[pgKnowledgeGraph.NodePropertyDescription.key]])

        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},fetched,{Logging.Object.OBJECT},node {nodeID}," + str(datetime.now()))
        return nodeDict, 200
    except Exception as e:
        loggerError.error("Error in logicForGetNodeViaID: " + str(e))
        return e, 500

##################################################
def logicForGetNodesByUniqueID(request:Request, nodeID:str) -> tuple[list[dict]|Exception, int]:
    """
    Retrieve all nodes with a certain unique ID

    """
    try:
        result = pgKnowledgeGraph.Basics.getNode(nodeID)
        if isinstance(result, Exception):
            raise result
        result = pgKnowledgeGraph.Basics.getAllNodesThatShareTheUniqueID(result.uniqueID)
        if isinstance(result, Exception):
            raise result
        
        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},fetched,{Logging.Object.OBJECT},unique nodes from {nodeID}," + str(datetime.now()))
        return result, 200
    except Exception as e:
        loggerError.error("Error in logicForGetNodesByUniqueID: " + str(e))
        return e, 500
    
##################################################
def logicForGetAssociatedResources(request:Request, nodeID:str, resourceType:str) -> tuple[list[dict]|Exception, int]:
    """
    Gather neighboring resources of a certain type from the KG
    
    """
    try:
        result = pgKnowledgeGraph.Basics.getSpecificNeighborsByType(nodeID, resourceType)
        if isinstance(result, Exception):
            raise result
        
        locale = ProfileManagementOrganization.getUserLocale(request.session)
        for elemIdx, elem in enumerate(result):
            for propIdx, prop in enumerate(elem[pgKnowledgeGraph.NodeDescription.properties]):
                result[elemIdx][pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.name] = manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,prop[pgKnowledgeGraph.NodePropertyDescription.key]])

        
        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},fetched,{Logging.Object.OBJECT},neighbor nodes of {nodeID} of type {resourceType}," + str(datetime.now()))
        return result, 200
    except Exception as e:
        loggerError.error("Error in logicForGetAssociatedResources: " + str(e))
        return e, 500
    
##################################################
def logicForGetNeighbors(request:Request, nodeID:str):
    """
    Gather all neighbors of a node inside an orga from the KG
    
    """
    try:
        result = pgKnowledgeGraph.Basics.getEdgesForNode(nodeID)
        if isinstance(result, Exception):
            raise result
        
        # remove nodes not belonging to the system
        filteredOutput = [entry for entry in result if entry[pgKnowledgeGraph.NodeDescription.createdBy] == pgKnowledgeGraph.defaultOwner]
        locale = ProfileManagementOrganization.getUserLocale(request.session)
        for elemIdx, elem in enumerate(filteredOutput):
            for propIdx, prop in enumerate(elem[pgKnowledgeGraph.NodeDescription.properties]):
                filteredOutput[elemIdx][pgKnowledgeGraph.NodeDescription.properties][propIdx][pgKnowledgeGraph.NodePropertyDescription.name] = manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,prop[pgKnowledgeGraph.NodePropertyDescription.key]])

        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},fetched,{Logging.Object.OBJECT},neighboring nodes of node {nodeID}," + str(datetime.now()))
        return filteredOutput, 200
    except Exception as e:
        loggerError.error("Error in logicForGetNeighbors: " + str(e))
        return e, 500

##################################################
def logicForAddNode(request:Request, validatedInput) -> tuple[dict|Exception, int]:
    """
    Add a new node to the KG
    
    """
    try:
        result = pgKnowledgeGraph.Basics.createNode(validatedInput)
        if isinstance(result, Exception):
            raise result
        
        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},node {result.nodeID}," + str(datetime.now()))

        return result.toDict(), 200
    except Exception as e:
        loggerError.error("Error in logicForAddNode: " + str(e))
        return e, 500
        

##################################################
def logicForCreateOrUpdateAndLinkNodes(request, validatedInput) -> tuple[None|Exception, int]:
    """
    Combined access for frontend to create and update together with linking
    
    """
    try:
        if validatedInput["type"] == "create":
            # create node for the system
            if "nodeID" in validatedInput["node"]:
                del validatedInput["node"]["nodeID"]
            resultNode = pgKnowledgeGraph.Basics.createNode(validatedInput["node"], pgKnowledgeGraph.defaultOwner)
            if isinstance(resultNode, Exception):
                raise resultNode
            # create edges
            for nodeIDFromEdge in validatedInput["edges"]["create"]:
                # check if node of the other side of the edge comes from the system and if so, create an orga copy of it
                otherNode = pgKnowledgeGraph.Basics.getNode(nodeIDFromEdge)
                if isinstance(otherNode, Exception):
                    raise otherNode

                # create edge to new node
                result = pgKnowledgeGraph.Basics.createEdge(otherNode.nodeID, resultNode.nodeID) 
                if isinstance(result, Exception):
                    raise result
            # remove edges
            for nodeIDFromEdge in validatedInput["edges"]["delete"]:
                result = pgKnowledgeGraph.Basics.deleteEdge(resultNode.nodeID, nodeIDFromEdge)
                if isinstance(result, Exception):
                    raise result

        elif validatedInput["type"] == "update":
            # update node
            resultNode = pgKnowledgeGraph.Basics.updateNode(validatedInput["node"]["nodeID"], validatedInput["node"])
            if isinstance(resultNode, Exception):
                raise resultNode
            # create edges
            for nodeIDFromEdge in validatedInput["edges"]["create"]:
                # create edge to new node
                result = pgKnowledgeGraph.Basics.createEdge(nodeIDFromEdge, resultNode.nodeID) 
                if isinstance(result, Exception):
                    raise result
            # remove edges
            for nodeIDFromEdge in validatedInput["edges"]["delete"]:
                result = pgKnowledgeGraph.Basics.deleteEdge(resultNode.nodeID, nodeIDFromEdge)
                if isinstance(result, Exception):
                    raise result
        else:
            return Response("Wrong type in input!", status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"{Logging.Subject.USER},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.EDITED},created or updated,{Logging.Object.OBJECT},nodes and edges," + str(datetime.now()))

        return None, 200
    except Exception as e:
        loggerError.error("Error in logicForCreateOrUpdateAndLinkNodes: " + str(e))
        return e, 500
    
##################################################
def logicForUpdateNode(request:Request, validatedInput) -> tuple[dict|Exception, int]:
    """
    Updates the values of a node
    
    """
    try:
        result = pgKnowledgeGraph.Basics.updateNode(validatedInput["nodeID"], validatedInput)
        if isinstance(result, Exception):
            raise result
        
        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.EDITED},updated,{Logging.Object.OBJECT},node {validatedInput['nodeID']}," + str(datetime.now()))
        return result.toDict(), 200
    except (Exception) as error:
        loggerError.error("Error in logicForUpdateNode: " + str(error))
        return error, 500
    
##################################################
def logicForDeleteNode(request:Request, nodeID:str) -> tuple[None|Exception, int]:
    """
    Deletes a node from the graph by ID

    """
    try:
        result = pgKnowledgeGraph.Basics.deleteNode(nodeID)
        if isinstance(result, Exception):
            raise result
        
        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},node {nodeID}," + str(datetime.now()))
        return None, 200
    except Exception as e:
        loggerError.error("Error in logicForDeleteNode: " + str(e))
        return e, 500

##################################################
def logicForAddEdge(request:Request, validatedInput) -> tuple[None|Exception, int]:
    """
    Add an edge to the KG
    
    """
    try:
        entityIDs = validatedInput["entityIDs"]
        ID1 = entityIDs[0]
        ID2 = entityIDs[1]

        result = pgKnowledgeGraph.Basics.createEdge(ID1, ID2) 
        if isinstance(result, Exception):
            raise result
        
        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},edge from {ID1} to {ID2}," + str(datetime.now()))

        return None, 200
    except Exception as e:
        loggerError.error("Error in logicForAddEdge: " + str(e))
        return e, 500
    
##################################################
def logicForDeleteEdge(request:Request, nodeID1:str, nodeID2:str) -> tuple[None|Exception, int]:
    """
    Deletes an edge from the KG
    
    """
    try:
        result = pgKnowledgeGraph.Basics.deleteEdge(nodeID1, nodeID2)
        if isinstance(result, Exception):
            raise result
        
        logger.info(f"{Logging.Subject.ADMIN},{ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},edge from {nodeID1} to {nodeID2}," + str(datetime.now()))
        return None, 200
    except Exception as e:
        loggerError.error("Error in logicForDeleteEdge: " + str(e))
        return e, 500