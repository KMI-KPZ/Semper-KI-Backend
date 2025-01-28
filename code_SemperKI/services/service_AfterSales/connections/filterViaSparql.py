"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions using the sparql queries to filter for contractors
"""

import copy, logging
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertyDescription
from code_SemperKI.modelFiles.processModel import Process, ProcessInterface

from ..connections.postgresql import pgKG
from ..definitions import *
from ..utilities.sparqlQueries import *

loggerError = logging.getLogger("errors")


##################################################
class Filter():
    """
    Filter and save results
    
    """

    ##################################################
    def __init__(self):
        """
        Init stuff
        
        """
        self.dummy = []
    
    ##################################################
    def getFilteredContractors(self, processObj:ProcessInterface|Process) -> list:
        """
        Get the filtered contractors

        :return: List of suitable contractors
        :rtype: list
        
        """
        try:
            ###
            outList = []
            return list(set(outList))
        except Exception as e:
            loggerError.error(f"Error in getFilteredContractors: {e}")
            raise e
