"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Am specific database knowledge graph stuff 
""" 

#from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import 

from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertiesTypesOfEntries, NodePropertyDescription
from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import Logic, Basics

from ...definitions import *

##################################################
def getPropertyDefinitionForNodeType(nodeType:str) -> list[dict]:
    """
    For different node types, different properties are important. 
    Retrieve those, especially for the Frontend.

    :param nodeType: The type of the node
    :type nodeType: str
    :return: A list of the properties, defined properly
    :rtype: list[dict] / JSON
    
    """
    outList = []
    match nodeType:
        case NodeTypesAS.organization:
            pass
    return outList

##################################################
class LogicAS(Logic):
    """
    Extending the class for AS usage
    
    """
    
    ##################################################
    @staticmethod
    def dummyLogic() -> None:
        """
        A dummy logic function
        
        """
        pass