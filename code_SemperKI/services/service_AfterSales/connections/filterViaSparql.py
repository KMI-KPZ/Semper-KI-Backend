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
            # self.resultGroups = [{} for i in range(len(processObj.serviceDetails[ServiceDetails.groups]))]
            # self.printerGroups = [{} for i in range(len(processObj.serviceDetails[ServiceDetails.groups]))]
            # for groupIdx, group in enumerate(processObj.serviceDetails[ServiceDetails.groups]):
            #     retVal = self.filterByMaterial(processObj.serviceDetails[ServiceDetails.groups][groupIdx][ServiceDetails.material], groupIdx)
            #     if isinstance(retVal, Exception):
            #         raise retVal
            #     chosenPostProcessings = processObj.serviceDetails[ServiceDetails.groups][groupIdx][ServiceDetails.postProcessings]
            #     if chosenPostProcessings != {}:
            #         retVal = self.filterByPostProcessings(chosenPostProcessings, groupIdx)
            #         if isinstance(retVal, Exception):
            #             raise retVal
            #     calculations = processObj.serviceDetails[ServiceDetails.groups][groupIdx][ServiceDetails.calculations]
            #     retVal = self.filterByPrinter(calculations, groupIdx)
            #     if isinstance(retVal, Exception):
            #         raise retVal
            # # TODO: do something with the information, that is inside every group. For now, just return the whole thing
            outList = []
            # for group in self.resultGroups:
            #     outList.extend(group.values())
            return list(set(outList))
        except Exception as e:
            loggerError.error(f"Error in getFilteredContractors: {e}")
            raise e
