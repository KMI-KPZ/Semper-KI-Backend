"""
Part of Semper-KI software

Silvio Weging 2024

Contains: The database backed knowledge graph
"""

import json, logging, copy, time
from datetime import datetime
from django.utils import timezone
from django.conf import settings

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient
from Generic_Backend.code_General.utilities.crypto import generateURLFriendlyRandomString

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.modelFiles.nodesModel import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
loggerPerformance = logging.getLogger("performance")
#######################################################

##################################################
def getNode(nodeID:str):
    """
    Gets a node by ID

    :param nodeID: The id of the node
    :type nodeID: str
    :return: Node or Error
    :rtype: Node|Exception	
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()

        node = Node.objects.get(nodeID=nodeID)
        	
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Get Node;{endPC-startPC};{endPT-startPT}")
        logger.info(f"Got node with id {nodeID}")
        return node
    except Exception as error:
        logger.error(f'could not get node: {str(error)}')
        return error

##################################################
def createNode(information:dict):
    """
    Creates a node

    :param information: What the node contains right from the start
    :type information: dict
    :return: Created Node or Error
    :rtype: Node|Exception
    
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()
        
        nodeID = generateURLFriendlyRandomString()
        nodeName = ""
        nodeType = ""
        context = ""
        properties = {}
        updatedWhen = timezone.now()

        for content in information:
            match content:
                case "nodeName":
                    nodeName = content[NodeDescription.nodeName]
                case "nodeType":
                    nodeType = content[NodeDescription.nodeType]
                case "context":
                    context = content[NodeDescription.context]
                case "properties":
                    properties = content[NodeDescription.properties]
                case _:
                    raise Exception("wrong content in information")
        
        createdNode = Node.objects.create(nodeID=nodeID, nodeName=nodeName, nodeType=nodeType, context=context, properties=properties, updatedWhen=updatedWhen)
        
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Create Node;{endPC-startPC};{endPT-startPT}")
        logger.info(f"Created node with id {nodeID}")
        return createdNode
    except (Exception) as error:
        logger.error(f'could not create node: {str(error)}')
        return error
        
##################################################
def updateNode(nodeID:str, information:dict):
    """
    This function updates the given node with the given information

    :param nodeID: the id of the node
    :type nodeID: str
    :param information: the information to update
    :type information: dict
    :return: The updated node or Exception
    :rtype: Node|Exception
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()

        node = Node.objects.get(nodeID=nodeID)
        for content in information:
            match content:
                case "nodeName":
                    node.nodeName = content[NodeDescription.nodeName]
                case "nodeType":
                    node.nodeType = content[NodeDescription.nodeType]
                case "context":
                    node.context = content[NodeDescription.context]
                case "properties":
                    node.properties = content[NodeDescription.properties]
                case _:
                    raise Exception("wrong content in information")
        node.save()
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Update Node;{endPC-startPC};{endPT-startPT}")
        logger.info(f"Updated node with id: {nodeID}")	
        return node
    except (Exception) as error:
        logger.error(f'could not update node: {str(error)}')
        return error	


##################################################
def deleteNode(nodeID:str):
    """
    Delete the node via ID

    :param nodeID: The id of the node
    :type nodeID: str
    :return: None | Exception
    :rtype: None | Exception
    
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()
        
        node = Node.objects.get(nodeID=nodeID)
        node.delete()

        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Delete Node;{endPC-startPC};{endPT-startPT}")
        logger.info(f'Deleted node with id {nodeID}')
        return None
    except (Exception) as error:
        logger.error(f'could not delete node: {str(error)}')
        return error

##################################################
def createEdge(nodeID1:str, nodeID2:str):
    """
    links two nodes together.
    
    :param nodeID1: nodeID1 ID of the first node.
    :type nodeID1: str
    :param nodeID2: nodeID2 ID of the second node.
    :type nodeID2: str
    :return: None | Exception
    :rtype: None | Exception
    """	
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()

        node1 = Node.objects.get(nodeID=nodeID1)
        node2 = Node.objects.get(nodeID=nodeID2)
        
        node1.edges.add(node2)
        node1.save()
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Create Edge;{endPC-startPC};{endPT-startPT}")
        logger.info(f"Linked nodes with id: {nodeID1} and {nodeID2}")	
        return None
    except (Exception) as error:
        logger.error(f'could not link the two nodes: {str(error)}')
        return error
    
##################################################
def deleteEdge(nodeID1:str, nodeID2:str):
    """
    deletes the edge between two nodes.
    
    :param nodeID1: nodeID1 ID of the first node.
    :type nodeID1: str
    :param nodeID2: nodeID2 ID of the second node.
    :type nodeID2: str
    :return: None | Exception
    :rtype: None | Exception
    """	
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()

        node1 = Node.objects.get(nodeID=nodeID1)
        node2 = Node.objects.get(nodeID=nodeID2)
        
        node1.edges.remove(node2)
        node1.save()
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Delete Edge;{endPC-startPC};{endPT-startPT}")
        logger.info(f"Unlinked nodes with id: {nodeID1} and {nodeID2}")	
        return None
    except (Exception) as error:
        logger.error(f'could not delete link between the two nodes: {str(error)}')
        return error

##################################################
def getNodesByType(nodeType:str) -> list[dict]:
    """
    Return all nodes with a given type

    :param nodeType: The type of the node
    :type nodeType: str
    :return: List with all nodes and their info
    :rtype: list of dicts
    
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()

        nodes = Node.objects.filter(nodeType=nodeType)
        outList = list()
        for entry in nodes:
            outList.append(entry.toDict())

        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Get Nodes By Type;{endPC-startPC};{endPT-startPT}")
        logger.info(f"Gathered all nodes by type: {nodeType}")	
        return outList
    except (Exception) as error:
        logger.error(f'could not get nodes by type: {str(error)}')
        return error

##################################################
def getNodesByProperty(property:str) -> list[dict]:
    """
    Return all nodes with a given property

    :param property: A specific property
    :type property: str
    :return: List with all nodes and their info
    :rtype: list of dicts
    
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()

        nodes = Node.objects.filter(properties__contains=property)
        outList = list()
        for entry in nodes:
            outList.append(entry.toDict())

        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Get Nodes By Property;{endPC-startPC};{endPT-startPT}")
        logger.info(f"Gathered all nodes by property: {property}")	
        return outList
    except (Exception) as error:
        logger.error(f'could not get nodes by property: {str(error)}')
        return error

##################################################
def getSpecificNeighborsByType(nodeID:str, neighborNodeType:str):
    """
    Return all neighbors that have the specified neighborNodeType

    :param nodeID: The ID of the node to look for neighbors
    :type nodeID: str
    :param neighborNodeType: The type of neighbor that we want to find
    :type neighborNodeType: str
    :return: list of neighbors
    :rtype: list	
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()
        
        outList = []
        for entry in Node.objects.filter(nodeID=nodeID):	
            for neighbor in entry.edges.filter(nodeType=neighborNodeType):
                outList.append(neighbor.toDict())
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Get Neighbors By Type;{endPC-startPC};{endPT-startPT}")
        logger.info(f"Gathered all neighbors for {nodeID} by type: {neighborNodeType}")	
        return outList
    except (Exception) as error:
        logger.error(f'could not get neighbors by type for node: {str(error)}')
        return error

##################################################
def getSpecificNeighborsByProperty(nodeID:str, neighborProperty:str):
    """
    Return all neighbors that have the specified neighborNodeType

    :param nodeID: The ID of the node to look for neighbors
    :type nodeID: str
    :param neighborProperty: The type of neighbor that we want to find
    :type neighborProperty: str
    :return: list of neighbors
    :rtype: list	
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()
        
        outList = []
        for entry in Node.objects.filter(nodeID=nodeID):	
            for neighbor in entry.edges.filter(properties__contains=neighborProperty):
                outList.append(neighbor.toDict())
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Get Neighbors By Property;{endPC-startPC};{endPT-startPT}")
        logger.info(f"Gathered all neighbors for {nodeID} by property: {neighborProperty}")	
        return outList
    except (Exception) as error:
        logger.error(f'could not get neighbors by property for node: {str(error)}')
        return error

##################################################
def getGraph():
    """
    Return the whole graph

    :return: The graph as Dictionary of nodes and edges
    :rtype: Dict
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()

        allNodes = Node.objects.all()
        outDict = {"nodes": [], "edges": []}
        for entry in allNodes:
            outDict["nodes"].append(entry.toDict())
            for neighbor in entry.edges.all():
                outDict["edges"].append([entry.nodeID,neighbor.nodeID])
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Generate Graph;{endPC-startPC};{endPT-startPT}")
        logger.info("Fetched the whole graph")	
        return outDict
    except (Exception) as error:
        logger.error(f'could not return graph: {str(error)}')
        return error
    
##################################################
def createGraph():
    pass #TODO
    
##################################################
def deleteGraph():
    """
    Delete the whole graph

    :return: None or Exception
    :rtype: None | Exception
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()

        Node.objects.delete()
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Delete Graph;{endPC-startPC};{endPT-startPT}")
        logger.info("Deleted the whole graph")	
        return None
    except (Exception) as error:
        logger.error(f'could not delete graph: {str(error)}')
        return error