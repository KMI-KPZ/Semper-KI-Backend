from __future__ import annotations 
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
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.modelFiles.nodesModel import *

logger = logging.getLogger("logToFile")
loggerConsole = logging.getLogger("django")
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
        loggerConsole.info(f"Got node with id {nodeID}")
        return node
    except Exception as error:
        loggerError.error(f'could not get node: {str(error)}')
        return error

##################################################
def createNode(information:dict, createdBy=defaultOwner):
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
                case "nodeID":
                    nodeID = information[NodeDescription.nodeID]
                case "nodeTempID":
                    pass
                case "nodeName":
                    nodeName = information[NodeDescription.nodeName]
                case "nodeType":
                    nodeType = information[NodeDescription.nodeType]
                case "context":
                    context = information[NodeDescription.context]
                case "properties":
                    assert isinstance(information[NodeDescription.properties], list), "Wrong type while adding properties to a node"
                    for entry in information[NodeDescription.properties]:
                        properties[entry[NodePropertyDescription.name]] = entry
                case _:
                    raise Exception("wrong content in information")

        createdNode, _ = Node.objects.update_or_create(nodeID=nodeID, defaults={"nodeName": nodeName, "nodeType": nodeType, "context": context, "properties": properties, "createdBy": createdBy, "updatedWhen": updatedWhen})
        
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Create Node;{endPC-startPC};{endPT-startPT}")
        loggerConsole.info(f"Created node with id {nodeID}")
        return createdNode
    except (Exception) as error:
        loggerError.error(f'could not create node: {str(error)}')
        return error
    
##################################################
def copyNode(node:Node, createdBy:str=defaultOwner):
    """
    Copy an existing node, therefore giving it a new creator and nodeiD

    :param node: The existing node
    :type node: Node
    :param createdBy: Who ordered the copy (usually an organization)
    :type createdBy: str
    :return: New Node
    :rtype: Node|Exception
    
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()
        
        nodeID = generateURLFriendlyRandomString()
        nodeName = node.nodeName
        nodeType = node.nodeType
        context = node.context
        properties = node.properties
        updatedWhen = timezone.now()

        createdNode, _ = Node.objects.update_or_create(nodeID=nodeID, defaults={"nodeName": nodeName, "nodeType": nodeType, "context": context, "properties": properties, "createdBy": createdBy, "updatedWhen": updatedWhen})
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Copy Node;{endPC-startPC};{endPT-startPT}")
        loggerConsole.info(f"Copied node with new id {nodeID}")
        return createdNode
    except (Exception) as error:
        loggerError.error(f'could not copy node: {str(error)}')
        return error
    
##################################################
def createOrganizationNode(orgaID:str):
    """
    Create a node for an organization

    :param orgaID: The ID of the organization
    :type orgaID: str
    :return: None
    :rtype: None
    
    """
    result = getNode(orgaID)
    if isinstance(result, Exception):
        orgaName = pgProfiles.ProfileManagementBase.getOrganizationName(orgaID)
        information = {NodeDescription.nodeID: orgaID, NodeDescription.nodeName: orgaName, NodeDescription.nodeType: NodeType.organization}
        createNode(information, orgaID)

###################################################################################
def deleteAllNodesFromOrganization(orgaID:str):
    """
    Gather all nodes belonging to an organization and delete them

    :param orgaID: The ID of the organization
    :type orgaID: str
    :return: None
    :rtype: None
    
    """
    try:
        nodes = getEdgesForNode(orgaID)
        if isinstance(nodes, Exception):
            raise nodes
        for entry in nodes:
            nodeID = entry[NodeDescription.nodeID]
            owner = entry[NodeDescription.createdBy]
            if owner == orgaID:
                result = deleteNode(nodeID)
                if isinstance(result, Exception):
                    raise result
        result = deleteNode(orgaID)
        if isinstance(result, Exception):
            raise result
    except Exception as error:
        logger.error(f"Could not delete nodes of orga: {error}")
        
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
                case NodeDescription.nodeID:
                    pass
                case NodeDescription.nodeName:
                    node.nodeName = information[NodeDescription.nodeName]
                case NodeDescription.nodeType:
                    node.nodeType = information[NodeDescription.nodeType]
                case NodeDescription.context:
                    node.context = information[NodeDescription.context]
                case NodeDescription.properties:
                    assert isinstance(information[NodeDescription.properties], list), "Wrong type while adding properties to a node"
                    for entry in information[NodeDescription.properties]:
                        if entry[NodePropertyDescription.value] == "":
                            del node.properties [entry[NodePropertyDescription.name]]
                        else:
                            node.properties[entry[NodePropertyDescription.name]] = entry
                case _:
                    raise Exception("wrong content in information")
        node.updatedWhen = timezone.now()
        node.save()
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Update Node;{endPC-startPC};{endPT-startPT}")
        loggerConsole.info(f"Updated node with id: {nodeID}")	
        return node
    except (Exception) as error:
        loggerError.error(f'could not update node: {str(error)}')
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
        loggerConsole.info(f'Deleted node with id {nodeID}')
        return None
    except (Exception) as error:
        loggerError.error(f'could not delete node: {str(error)}')
        return error
    
##################################################
def getEdgesForNode(nodeID:str) -> list[dict]:
    """
    Return all neighbors to a node

    :param nodeID: The id of the node
    :type nodeID: str
    :return: List with all neighbors and their info
    :rtype: list of dicts
    
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()

        node = Node.objects.get(nodeID=nodeID)
        outList = list()
        for entry in node.edges.all():
            outList.append(entry.toDict())

        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Get Edges;{endPC-startPC};{endPT-startPT}")
        loggerConsole.info(f"Gathered all neighbors of: {nodeID}")	
        return outList
    except (Exception) as error:
        loggerError.error(f'could not get neighbors: {str(error)}')
        return error
    
##################################################
def getIfEdgeExists(node1ID:str, node2ID) -> bool:
    """
    Return if an edge exists

    :param node1ID: The id of the first node
    :type node1ID: str
    :param node2ID: The id of the second node
    :type node2ID: str
    :return: If edge exists or not
    :rtype: bool
    
    """
    try:
        startPC = time.perf_counter_ns()
        startPT = time.process_time_ns()

        node1 = Node.objects.get(nodeID=node1ID)
        node2 = Node.objects.get(nodeID=node2ID)
        isInside = False
        if node2 in node1.edges.all():
            isInside = True
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Get Edge;{endPC-startPC};{endPT-startPT}")
        loggerConsole.info(f"Checked if edge existed between: {node1ID} {node2ID}")	
        return isInside
    except (Exception) as error:
        loggerError.error(f'could not check if edge exists: {str(error)}')
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
        node1.updatedWhen = timezone.now()
        node1.save()
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Create Edge;{endPC-startPC};{endPT-startPT}")
        loggerConsole.info(f"Linked nodes with id: {nodeID1} and {nodeID2}")	
        return None
    except (Exception) as error:
        loggerError.error(f'could not link the two nodes: {str(error)}')
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
        loggerConsole.info(f"Unlinked nodes with id: {nodeID1} and {nodeID2}")	
        return None
    except (Exception) as error:
        loggerError.error(f'could not delete link between the two nodes: {str(error)}')
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
        loggerConsole.info(f"Gathered all nodes by type: {nodeType}")	
        return outList
    except (Exception) as error:
        loggerError.error(f'could not get nodes by type: {str(error)}')
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

        nodes = Node.objects.filter(properties__icontains=property)
        outList = list()
        for entry in nodes:
            outList.append(entry.toDict())

        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Get Nodes By Property;{endPC-startPC};{endPT-startPT}")
        loggerConsole.info(f"Gathered all nodes by property: {property}")	
        return outList
    except (Exception) as error:
        loggerError.error(f'could not get nodes by property: {str(error)}')
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
        node = Node.objects.get(nodeID=nodeID)	
        for neighbor in node.edges.filter(nodeType=neighborNodeType):
            outList.append(neighbor.toDict())
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Get Neighbors By Type;{endPC-startPC};{endPT-startPT}")
        loggerConsole.info(f"Gathered all neighbors for {nodeID} by type: {neighborNodeType}")	
        return outList
    except (Exception) as error:
        loggerError.error(f'could not get neighbors by type for node: {str(error)}')
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
        node = Node.objects.get(nodeID=nodeID)	
        for neighbor in node.edges.filter(properties__icontains=neighborProperty):
            outList.append(neighbor.toDict())
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Get Neighbors By Property;{endPC-startPC};{endPT-startPT}")
        loggerConsole.info(f"Gathered all neighbors for {nodeID} by property: {neighborProperty}")	
        return outList
    except (Exception) as error:
        loggerError.error(f'could not get neighbors by property for node: {str(error)}')
        return error

##################################################
def getGraph():
    """
    Return the whole graph

    :return: The graph as Dictionary of nodes and edges
    :rtype: Dict | Exception
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
        loggerConsole.info("Fetched the whole graph")	
        return outDict
    except (Exception) as error:
        loggerError.error(f'could not return graph: {str(error)}')
        return error
    
##################################################
def createGraph(graph:list):
    """
    Create graph from input

    :param graph: The graph
    :type graph: list of the nodes and their edges
    :return: Created Graph or Exception
    :rtype: Dict | Exception
    """
    try:
        alreadySeenNodes = {}
        for entry in graph:
            node = entry["node"]
            
            # dont create a node twice
            if node["nodeTempID"] not in alreadySeenNodes:
                node1 = createNode(node)
                if isinstance(node1, Exception):
                    raise node1
                alreadySeenNodes[node["nodeTempID"]] = node1.nodeID
            else:
                node1 = getNode(alreadySeenNodes[node["nodeTempID"]])

            for neighbor in entry["edges"]:
                if neighbor["nodeTempID"] not in alreadySeenNodes:
                    node2 = createNode(neighbor)
                    if isinstance(node2, Exception):
                        raise node2
                    alreadySeenNodes[neighbor["nodeTempID"]] = node2.nodeID
                else:
                    node2 = getNode(alreadySeenNodes[neighbor["nodeTempID"]])
                
                result = createEdge(node1.nodeID, node2.nodeID)
                if isinstance(result, Exception):
                    raise result
        newGraph = getGraph()
        if isinstance(newGraph, Exception):
            raise newGraph
        return newGraph
    except (Exception) as error:
        loggerError.error(f'could not create graph: {str(error)}')
        return error
    
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

        Node.objects.all().delete()
        
        endPC = time.perf_counter_ns()
        endPT = time.process_time_ns()
        loggerPerformance.info(f"DB;Delete Graph;{endPC-startPC};{endPT-startPT}")
        loggerConsole.info("Deleted the whole graph")	
        return None
    except (Exception) as error:
        loggerError.error(f'could not delete graph: {str(error)}')
        return error
    