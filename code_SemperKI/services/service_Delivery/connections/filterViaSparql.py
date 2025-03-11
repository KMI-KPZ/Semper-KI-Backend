"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions using the sparql queries to filter for contractors
"""

import copy, logging
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertyDescription
from code_SemperKI.modelFiles.processModel import Process, ProcessInterface
from code_SemperKI.definitions import ContractorParsingForFrontend

from Generic_Backend.code_General.modelFiles.organizationModel import OrganizationDescription
from Generic_Backend.code_General.connections.postgresql import pgProfiles

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
    
    ##################################################
    def filterDContractors(self, processObj:ProcessInterface|Process) -> list|Exception:
        """
        get all contractors for the given process
        
        :param processObj: Process object
        :type processObj: ProcessInterface|Process
        :return: List of contractors
        :rtype: List
        """
        try:
            serviceType = processObj.serviceType
            orgalist = pgProfiles.ProfileManagementBase.getOrganisationWithSupportedService(serviceType)
            listOfContractors = [orga.hashedID for orga in orgalist]
            return listOfContractors
        except Exception as e:
            loggerError.error(f"Error in filterDContractors: {e}")
            raise e

    ##################################################
    def getFilteredContractors(self, processObj:ProcessInterface|Process) -> dict:
        """
        Get the filtered contractors

        :return: List of suitable contractors
        :rtype: list
        
        """
        try:
            listOfContractors = self.filterDContractors(processObj)
            if isinstance(listOfContractors, Exception):
                raise listOfContractors
            
            return {ContractorParsingForFrontend.contractors:listOfContractors, ContractorParsingForFrontend.errors: []}
        except Exception as e:
            loggerError.error(f"Error in getFilteredContractors: {e}")
            raise e
