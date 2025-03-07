from __future__ import annotations

"""
Part of Semper-KI software

Silvio Weging 2024

Contains: The database backed knowledge graph
"""

import json, logging, copy, time
from datetime import datetime
from difflib import SequenceMatcher
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

#Class for basic access
##################################################
class Basics():
    """
    Basis access to the model
    
    """
    ##################################################
    @staticmethod
    def getNode(nodeID:str):
        """
        Gets a node by ID

        :param nodeID: The id of the node
        :type nodeID: str
        :return: Node or Error
        :rtype: Node|Exception	
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            node = Node.objects.get(nodeID=nodeID)
                
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Node;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Got node with id {nodeID}")
            return node
        except Exception as error:
            loggerError.error(f'could not get node: {str(error)}')
            return error

    ##################################################
    @staticmethod
    def createNode(information:dict, createdBy=defaultOwner, existingNodeID:str=""):
        """
        Creates a node

        :param information: What the node contains right from the start
        :type information: dict
        :return: Created Node or Error
        :rtype: Node|Exception
        
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()
            
            if existingNodeID != "":
                nodeID = existingNodeID
            else:
                nodeID = generateURLFriendlyRandomString()
            uniqueID = nodeID
            nodeName = ""
            nodeType = ""
            context = ""
            properties = {}
            clonedFrom = ""
            active = True
            updatedWhen = timezone.now()

            for content in information:
                match content:
                    case NodeDescription.nodeID:
                        uniqueID = information[NodeDescription.nodeID] # it's a clone
                    case "nodeTempID": # for testGraph
                        pass
                    case NodeDescription.nodeName:
                        nodeName = information[NodeDescription.nodeName]
                    case NodeDescription.nodeType:
                        nodeType = information[NodeDescription.nodeType]
                    case NodeDescription.context:
                        context = information[NodeDescription.context]
                    case NodeDescription.active:
                        active = information[NodeDescription.active]
                    case NodeDescription.properties:
                        assert isinstance(information[NodeDescription.properties], list), "Wrong type while adding properties to a node"
                        for entry in information[NodeDescription.properties]:
                            properties[entry[NodePropertyDescription.key]] = entry
                    case _:
                        pass

            createdNode, _ = Node.objects.update_or_create(nodeID=nodeID, defaults={"uniqueID": uniqueID, "nodeName": nodeName, "nodeType": nodeType, "context": context, "properties": properties, "createdBy": createdBy, "clonedFrom": clonedFrom, "active": active, "updatedWhen": updatedWhen})
            
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Create Node;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Created node with id {nodeID}")
            return createdNode
        except (Exception) as error:
            loggerError.error(f'could not create node: {str(error)}')
            return error
        
    ##################################################
    @staticmethod
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
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()
            
            nodeID = generateURLFriendlyRandomString()
            uniqueID = node.uniqueID
            nodeName = node.nodeName
            nodeType = node.nodeType
            context = node.context
            properties = node.properties
            clonedFrom = node.nodeID
            updatedWhen = timezone.now()

            createdNode, _ = Node.objects.update_or_create(nodeID=nodeID, defaults={"uniqueID": uniqueID, "nodeName": nodeName, "nodeType": nodeType, "context": context, "properties": properties, "createdBy": createdBy, "clonedFrom": clonedFrom, "updatedWhen": updatedWhen})
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Copy Node;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Copied node with new id {nodeID}")
            return createdNode
        except (Exception) as error:
            loggerError.error(f'could not copy node: {str(error)}')
            return error
        
    ##################################################
    @staticmethod
    def copyGraphForNewOwner(createdBy:str=defaultOwner):
        """
        Copy the whole graph for another owner
        
        :param createdBy: The new owner
        :type createdBy: str
        :return: None
        :rtype: None | Exception
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()
            
            nodes = Node.objects.all()
            for node in nodes:
                newNode = Basics.copyNode(node, createdBy)
                if isinstance(newNode, Exception):
                    raise newNode
                edges = node.edges.all()
                for edge in edges:
                    result = Basics.createEdge(newNode.nodeID, edge.nodeID)
                    if isinstance(result, Exception):
                        raise result
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Copy Graph;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Graph copied for new owner: {createdBy}")
            return None

        except Exception as error:
            loggerError.error(f"Could not copy graph for new owner: {error}")
            return error
        
    ##################################################
    @staticmethod
    def createOrganizationNode(orgaID:str):
        """
        Create a node for an organization

        :param orgaID: The ID of the organization
        :type orgaID: str
        :return: None
        :rtype: None
        
        """
        result = Basics.getNode(orgaID)
        if isinstance(result, Exception):
            orgaName = pgProfiles.ProfileManagementBase.getOrganizationName(orgaID)
            information = {NodeDescription.nodeID: orgaID, NodeDescription.nodeName: orgaName, NodeDescription.nodeType: NodeType.organization}
            Basics.createNode(information, orgaID, orgaID)

    ###################################################################################
    @staticmethod
    def deleteAllNodesFromOrganization(orgaID:str):
        """
        Gather all nodes belonging to an organization and delete them

        :param orgaID: The ID of the organization
        :type orgaID: str
        :return: None
        :rtype: None
        
        """
        try:
            nodes = Basics.getEdgesForNode(orgaID)
            if isinstance(nodes, Exception):
                raise nodes
            for entry in nodes:
                nodeID = entry[NodeDescription.nodeID]
                owner = entry[NodeDescription.createdBy]
                if owner == orgaID:
                    result = Basics.deleteNode(nodeID)
                    if isinstance(result, Exception):
                        raise result
            result = Basics.deleteNode(orgaID)
            if isinstance(result, Exception):
                raise result
        except Exception as error:
            loggerError.error(f"Could not delete nodes of orga: {error}")
            
    ##################################################
    @staticmethod
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
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

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
                    case NodeDescription.active:
                        node.active = information[NodeDescription.active]
                    case NodeDescription.properties:
                        assert isinstance(information[NodeDescription.properties], list), "Wrong type while adding properties to a node"
                        node.properties = {}
                        for entry in information[NodeDescription.properties]:
                            node.properties[entry[NodePropertyDescription.key]] = entry
                    case _:
                        pass
            node.updatedWhen = timezone.now()
            node.save()
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Update Node;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Updated node with id: {nodeID}")	
            return node
        except (Exception) as error:
            loggerError.error(f'could not update node: {str(error)}')
            return error	


    ##################################################
    @staticmethod
    def deleteNode(nodeID:str):
        """
        Delete the node via ID

        :param nodeID: The id of the node
        :type nodeID: str
        :return: None | Exception
        :rtype: None | Exception
        
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()
            
            node = Node.objects.get(nodeID=nodeID)
            node.delete()

            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Delete Node;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f'Deleted node with id {nodeID}')
            return None
        except (Exception) as error:
            loggerError.error(f'could not delete node: {str(error)}')
            return error
        
    ##################################################
    @staticmethod
    def getEdgesForNode(nodeID:str) -> list[dict]:
        """
        Return all neighbors to a node

        :param nodeID: The id of the node
        :type nodeID: str
        :return: List with all neighbors and their info
        :rtype: list of dicts
        
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            node = Node.objects.get(nodeID=nodeID)
            outList = list()
            for entry in node.edges.all():
                outList.append(entry.toDict())

            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Edges;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Gathered all neighbors of: {nodeID}")	
            return outList
        except (Exception) as error:
            loggerError.error(f'could not get neighbors: {str(error)}')
            return error
        
    ##################################################
    @staticmethod
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
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            node1 = Node.objects.get(nodeID=node1ID)
            node2 = Node.objects.get(nodeID=node2ID)
            isInside = False
            if node2 in node1.edges.all():
                isInside = True
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Edge;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Checked if edge existed between: {node1ID} {node2ID}")	
            return isInside
        except (Exception) as error:
            loggerError.error(f'could not check if edge exists: {str(error)}')
            return error

    ##################################################
    @staticmethod
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
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            node1 = Node.objects.get(nodeID=nodeID1)
            node2 = Node.objects.get(nodeID=nodeID2)
            
            node1.edges.add(node2)
            node1.updatedWhen = timezone.now()
            node1.save()
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Create Edge;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Linked nodes with id: {nodeID1} and {nodeID2}")	
            return None
        except (Exception) as error:
            loggerError.error(f'could not link the two nodes: {str(error)}')
            return error
        
    ##################################################
    @staticmethod
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
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            node1 = Node.objects.get(nodeID=nodeID1)
            node2 = Node.objects.get(nodeID=nodeID2)
            
            node1.edges.remove(node2)
            node1.save()
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Delete Edge;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Unlinked nodes with id: {nodeID1} and {nodeID2}")	
            return None
        except (Exception) as error:
            loggerError.error(f'could not delete link between the two nodes: {str(error)}')
            return error

    ##################################################
    @staticmethod
    def getNodesByType(nodeType:str) -> list[dict]:
        """
        Return all nodes with a given type

        :param nodeType: The type of the node
        :type nodeType: str
        :return: List with all nodes and their info
        :rtype: list of dicts
        
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            nodes = Node.objects.filter(nodeType=nodeType)
            outList = list()
            for entry in nodes:
                outList.append(entry.toDict())

            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Nodes By Type;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Gathered all nodes by type: {nodeType}")	
            return outList
        except (Exception) as error:
            loggerError.error(f'could not get nodes by type: {str(error)}')
            return error
    
    ##################################################
    @staticmethod
    def getSystemNodesByType(nodeType:str) -> list[dict]:
        """
        Return all nodes with a given type from the system

        :param nodeType: The type of the node
        :type nodeType: str
        :return: List with all nodes and their info
        :rtype: list of dicts
        
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            nodes = Node.objects.filter(nodeType=nodeType).filter(createdBy=defaultOwner)
            outList = list()
            for entry in nodes:
                outList.append(entry.toDict())

            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Nodes By Type;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Gathered all nodes by type: {nodeType}")	
            return outList
        except (Exception) as error:
            loggerError.error(f'could not get nodes by type: {str(error)}')
            return error

    ##################################################
    @staticmethod
    def getNodesByProperty(property:str) -> list[dict]:
        """
        Return all nodes with a given property

        :param property: A specific property
        :type property: str
        :return: List with all nodes and their info
        :rtype: list of dicts
        
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            nodes = Node.objects.filter(properties__icontains=property)
            outList = list()
            for entry in nodes:
                outList.append(entry.toDict())

            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Nodes By Property;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Gathered all nodes by property: {property}")	
            return outList
        except (Exception) as error:
            loggerError.error(f'could not get nodes by property: {str(error)}')
            return error
        
    ##################################################
    @staticmethod
    def getNodesByTypeAndProperty(nodeType:str, nodeProperty:str):
        """
        Return all nodes of a given type with a certain property

        :param nodeType: The node type
        :type nodeType: str
        :param nodeProperty: A specific property
        :type nodeProperty: str
        :return: List with all nodes and their info
        :rtype: list of dicts
        
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            nodes = Node.objects.filter(nodeType=nodeType).filter(properties__icontains=nodeProperty)
            outList = list()
            for entry in nodes:
                outList.append(entry.toDict())

            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Nodes By type and property;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Gathered all nodes by type and property: {nodeProperty}")	
            return outList
        except (Exception) as error:
            loggerError.error(f'could not get nodes of type {nodeType} by property {nodeProperty}: {str(error)}')
            return error
        
    ##################################################
    @staticmethod
    def getNodesByTypeAndPropertyAndValue(nodeType:str, nodeProperty:str, value:str):
        """
        Return all nodes of a given type with a certain property
        UNUSED

        :param nodeType: The node type
        :type nodeType: str
        :param nodeProperty: A specific property
        :type nodeProperty: str
        :param value: The value that is searched
        :type value: str
        :return: List with all nodes and their info
        :rtype: list of dicts
        
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            nodes = Node.objects.filter(nodeType=nodeType).filter(properties__icontains=nodeProperty).filter(properties__icontains=value) #"name": "buildVolume", "value": "400x400x400",
            outList = list()
            for entry in nodes:
                outList.append(entry.toDict())

            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Nodes By type and property and value;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Gathered all nodes by type and property and value: {nodeProperty}")	
            return outList
        except (Exception) as error:
            loggerError.error(f'could not get nodes of type {nodeType} by property {nodeProperty} and value {value}: {str(error)}')
            return error

    ##################################################
    @staticmethod
    def getSpecificNeighborsByType(nodeID:str, neighborNodeType:str) -> list[dict]|Exception:
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
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()
            
            outList = []
            node = Node.objects.get(nodeID=nodeID)	
            for neighbor in node.edges.filter(nodeType=neighborNodeType):
                outList.append(neighbor.toDict())
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Neighbors By Type;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Gathered all neighbors for {nodeID} by type: {neighborNodeType}")	
            return outList
        except (Exception) as error:
            loggerError.error(f'could not get neighbors by type for node: {str(error)}')
            return error

    ##################################################
    @staticmethod
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
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()
            
            outList = []
            node = Node.objects.get(nodeID=nodeID)	
            for neighbor in node.edges.filter(properties__icontains=neighborProperty):
                outList.append(neighbor.toDict())
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Neighbors By Property;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Gathered all neighbors for {nodeID} by property: {neighborProperty}")	
            return outList
        except (Exception) as error:
            loggerError.error(f'could not get neighbors by property for node: {str(error)}')
            return error
        
    ##################################################
    @staticmethod
    def getAllNodesThatShareTheUniqueID(uniqueID:str):
        """
        Gather all nodes that share a unique ID

        :param uniqueID: The ID that is unique across all copies
        :type uniqueID: str
        :return: list of nodes in dict format
        :rtype: list[dict] | Exception
        
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()
            
            outList = []
            nodes = Node.objects.filter(uniqueID=uniqueID)	
            for node in nodes:
                outList.append(node.toDict())
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Get Nodes with same uniqueID;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info(f"Gathered all nodes with the unique ID {uniqueID}")	
            return outList
        except (Exception) as error:
            loggerError.error(f'could not get all nodes with the same unqiue ID: {str(error)}')
            return error


    ##################################################
    @staticmethod
    def getGraph(createdBy="", allowedNodeTypes:list[str]=[]):
        """
        Return the whole graph

        :return: The graph as Dictionary of nodes and edges
        :rtype: Dict | Exception
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            allNodes = Node.objects.all()
            outDict = {"nodes": [], "edges": []}
            for entry in allNodes:
                if createdBy != "" and entry.createdBy != createdBy and entry.nodeType not in allowedNodeTypes:
                    continue
                outDict["nodes"].append(entry.toDict())
                for neighbor in entry.edges.all():
                    if createdBy != "" and neighbor.createdBy != createdBy and neighbor.nodeType not in allowedNodeTypes:
                        continue
                    outDict["edges"].append([entry.nodeID,neighbor.nodeID])
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Generate Graph;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info("Fetched the whole graph")	
            return outDict
        except (Exception) as error:
            loggerError.error(f'could not return graph: {str(error)}')
            return error
        
    ##################################################
    @staticmethod
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
                    node1 = Basics.createNode(node)
                    if isinstance(node1, Exception):
                        raise node1
                    alreadySeenNodes[node["nodeTempID"]] = node1.nodeID
                else:
                    node1 = Basics.getNode(alreadySeenNodes[node["nodeTempID"]])

                for neighbor in entry["edges"]:
                    if neighbor["nodeTempID"] not in alreadySeenNodes:
                        node2 = Basics.createNode(neighbor)
                        if isinstance(node2, Exception):
                            raise node2
                        alreadySeenNodes[neighbor["nodeTempID"]] = node2.nodeID
                    else:
                        node2 = Basics.getNode(alreadySeenNodes[neighbor["nodeTempID"]])
                    
                    result = Basics.createEdge(node1.nodeID, node2.nodeID)
                    if isinstance(result, Exception):
                        raise result
            newGraph = Basics.getGraph()
            if isinstance(newGraph, Exception):
                raise newGraph
            return newGraph
        except (Exception) as error:
            loggerError.error(f'could not create graph: {str(error)}')
            return error
        
    ##################################################
    @staticmethod
    def deleteGraph():
        """
        Delete the whole graph

        :return: None or Exception
        :rtype: None | Exception
        """
        try:
            # startPC = time.perf_counter_ns()
            # startPT = time.process_time_ns()

            Node.objects.all().delete()
            
            # endPC = time.perf_counter_ns()
            # endPT = time.process_time_ns()
            # loggerPerformance.info(f"DB;Delete Graph;{endPC-startPC};{endPT-startPT}")
            loggerConsole.info("Deleted the whole graph")	
            return None
        except (Exception) as error:
            loggerError.error(f'could not delete graph: {str(error)}')
            return error

##################################################
# Class for logic queries like build-volumes
class Logic():
    """
    Everything that requires some calculation or logic behind it
    
    """
    ##################################################
    @staticmethod
    def checkIfPropertyIsSimilar(property1:dict, property2:dict) -> bool|None:
        """
        Check if two properties are similar
        
        """
        try:
            # ignore certain keys
            if property1[NodePropertyDescription.key] in [NodeProperties.imgPath]:
                return None

            # check if the keys are the same
            if property1[NodePropertyDescription.key] != property2[NodePropertyDescription.key]:
                return False

            # if so, check the type (number, text and so on)
            if property1[NodePropertyDescription.type] != property2[NodePropertyDescription.type]:
                return False

            # if the type is the same, check the value. In case of numbers use some epsilon
            if property1[NodePropertyDescription.type] == NodePropertiesTypesOfEntries.number:
                if abs(float(property1[NodePropertyDescription.value]) - float(property2[NodePropertyDescription.value])) > 0.1:
                    return False
            elif property1[NodePropertyDescription.type] == NodePropertiesTypesOfEntries.text or property1[NodePropertyDescription.type] == NodePropertiesTypesOfEntries.string:
                if SequenceMatcher(a=property1[NodePropertyDescription.value], b=property2[NodePropertyDescription.value]).quick_ratio() < 0.8:
                    return False
            elif property1[NodePropertyDescription.type] == NodePropertiesTypesOfEntries.array:
                firstArray = property1[NodePropertyDescription.value].split(",")
                secondArray = property2[NodePropertyDescription.value].split(",")
                if len(firstArray) != len(secondArray):
                    return False
                for entry in firstArray:
                    if entry not in secondArray:
                        return False
            
            return True
        except Exception as error:
            loggerError.error(f"Could not check if properties are similar: {error}")
            return

    ##################################################
    @staticmethod
    def checkAndUpdateProperties(properties:dict, propertiesToCompareTo:dict) -> tuple[bool,float,list[dict]|Exception]:
        """
        Check if properties are similar or not. If so, update them if necessary. Return both the properties and if they are similar
        
        """
        try:
            outDict = {}
            similar = 0
            different = 0
            total = 0
            # check if the properties are the same
            for propKey, prop in properties.items():
                if propKey in propertiesToCompareTo:
                    result = Logic.checkIfPropertyIsSimilar(prop, propertiesToCompareTo[propKey])
                    if result is not None:
                        if result:
                            similar += 1
                        else:
                            different += 1
                        total += 1
                        outDict[propKey] = prop
                    else:
                        outDict[propKey] = propertiesToCompareTo[propKey]
                else:
                    outDict[propKey] = prop
            
            # calculate similarity via F1 Score
            if similar == 0:
                return False, 0., []
            precision = similar/(similar + different)
            recall = similar/total
            f1Score = 2. * (precision * recall) / (precision + recall)
            if f1Score > 0.8:
                # fill in the missing properties
                outList = []
                for propKey, prop in propertiesToCompareTo.items():
                    if propKey not in outDict:
                        outList.append(prop)
                    else:
                        outList.append(outDict[propKey])
                return True, f1Score, outList
            return False, f1Score, []
        except Exception as error:
            loggerError.error(f"Could not check and update properties: {error}")
            return False, 0., error
        
    ##################################################
    @staticmethod
    def similarityHelper(listOfNodes:list[dict], node:Node) -> bool|Exception:
        """
        Helper function for the similarity check

        :param listOfNodes: List of nodes to check for similarity
        :type listOfNodes: list[dict]
        :param node: The node to which the similarity is checked
        :type node: Node
        :return: If a similar node was found or not
        :rtype: bool | Exception
        
        """
        try:
            similarityList = []
            systemEdgesOfNode = Basics.getEdgesForNode(node.nodeID)
            systemEdgesOfNode = {entry[NodeDescription.nodeID]: entry for entry in systemEdgesOfNode if entry[NodeDescription.createdBy] == defaultOwner}
            # if there is, check if properties of the system node needs to be updated
            for entry in listOfNodes:
                if entry[NodeDescription.nodeID] == node.nodeID or entry[NodeDescription.createdBy] != defaultOwner:
                    continue
                # but first check if other linked nodes are the same (categories and such)
                if len(systemEdgesOfNode) != 0:
                    eligible = True
                    edges = Basics.getEdgesForNode(entry[NodeDescription.nodeID])
                    edges = {entry[NodeDescription.nodeID]: entry for entry in edges if entry[NodeDescription.createdBy] == defaultOwner}
                    for edge in systemEdgesOfNode:
                        if edge not in edges:
                            eligible = False
                            break
                    if not eligible:
                        continue

                # get properties
                entryProps = Basics.getNode(entry[NodeDescription.nodeID]).properties
                # check if properties are the same
                similar, f1Score, newProperties = Logic.checkAndUpdateProperties(node.properties, entryProps)
                if isinstance(newProperties, Exception):
                    raise newProperties
                if similar:
                    similarityList.append((entry[NodeDescription.nodeID], f1Score, newProperties))
            if len(similarityList) == 0:
                return False
            # get the best match
            similarityList.sort(key=lambda x: x[1], reverse=True)
            entry = similarityList[0]
            newProperties = entry[2]
            nodeIDOfMostSimilar = entry[0]
            # update the properties of the system node
            outNode = Basics.updateNode(nodeIDOfMostSimilar, {NodeDescription.properties: newProperties})
            if isinstance(outNode, Exception):
                raise outNode
            # change the uniqueID to the one from the system
            node.uniqueID = outNode.uniqueID
            node.save()
            return True
        except Exception as error:
            return error
    ##################################################
    @staticmethod
    def checkIfSimilarNodeExists(nodeID:str) -> Node|Exception:
        """
        Check if a similar node already exists
        
        """
        try:
            # fetch node
            node = Basics.getNode(nodeID)
            done = False
            outNode = None

            # check if there already is a system node within the uniqueIDs
            nodesWithTheSameUniqueID = Basics.getAllNodesThatShareTheUniqueID(node.uniqueID)
            if isinstance(nodesWithTheSameUniqueID, Exception):
                raise nodesWithTheSameUniqueID
            done = Logic.similarityHelper(nodesWithTheSameUniqueID, node)
            
            # if not, look for similar nodes in the system via checking the nodeType and properties
            if not done:
                nodesWithTheSameType = Basics.getSystemNodesByType(node.nodeType)
                if isinstance(nodesWithTheSameType, Exception):
                    raise nodesWithTheSameType
                done = Logic.similarityHelper(nodesWithTheSameType, node)
                if isinstance(done, Exception):
                    raise done

            # if there is no similar node, create a new one in the system and copy the properties + add edges
            if not done:
                outNode = Basics.copyNode(node)
                if isinstance(outNode, Exception):
                    raise outNode
                # create edges to other system nodes
                edges = Basics.getEdgesForNode(nodeID)
                if isinstance(edges, Exception):
                    raise edges
                for edge in edges:
                    if edge[NodeDescription.createdBy] == defaultOwner:
                        exc = Basics.createEdge(outNode.nodeID, edge[NodeDescription.nodeID])
                        if isinstance(exc, Exception):
                            raise exc
                done = True
            # return the node
            if done:
                return outNode
            else:
                raise Exception("System node was not created") # this should never happen
        except Exception as error:
            loggerError.error(f"Could not check if similar node exists: {error}")
            return error
                        