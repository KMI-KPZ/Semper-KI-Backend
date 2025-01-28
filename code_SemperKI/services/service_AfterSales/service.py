"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.serviceManager as Semper
from code_SemperKI.modelFiles.processModel import ProcessInterface, Process

from .connections.postgresql.pgService import initializeService as AS_initializeService, updateServiceDetails as AS_updateServiceDetails, deleteServiceDetails as AS_deleteServiceDetails, isFileRelevantForService as AS_isFileRelevantForService, serviceReady as AS_serviceReady, cloneServiceDetails as AS_cloneServiceDetails
#from .handlers.public.checkService import checkIfSelectionIsAvailable as AS_checkIfSelectionIsAvailable
from  .logics.checkServiceLogic import checkifSelectionIsAvailable as AS_checkIfSelectionIsAvailable
from .connections.filterViaSparql import *
from .definitions import SERVICE_NAME, SERVICE_NUMBER
#from .logics.costs import Costs

###################################################
class AfterSales(Semper.ServiceBase):
    """
    All connections of this service that Semper-KI should know about
    
    """

    ###################################################
    def initializeServiceDetails(self, serviceDetails:dict) -> None:
        """
        Initialize the service

        """
        return AS_initializeService(serviceDetails)

    ###################################################
    def updateServiceDetails(self, existingContent, newContent):
        """
        Run service specific update of service details

        """

        return AS_updateServiceDetails(existingContent, newContent)
    
    ###################################################
    def deleteServiceDetails(self, existingContent, deletedContent):
        """
        Delete stuff from a service

        """

        return AS_deleteServiceDetails(existingContent, deletedContent)
    
    ###################################################
    def isFileRelevantForService(self, existingContent, fileID:str) -> bool:
        """
        Check if a file is relevant for the service

        """
        return AS_isFileRelevantForService(existingContent, fileID)
    
    ###################################################
    def parseServiceDetails(self, existingContent) -> dict:
        """
        Parse the service details for Frontend

        """
        outContent = {}

        return outContent
    
    ###################################################
    def serviceReady(self, existingContent) -> tuple[bool, list[str]]:
        """
        Checks, if service is completely defined
        
        """
        return AS_serviceReady(existingContent)
    
    ###################################################
    def checkIfSelectionIsAvailable(self, processObj) -> bool:
        """
        Checks, if the selection of the service is available (material, ...)
        
        """
        completeOrNot, listOfMissingStuff =  AS_checkIfSelectionIsAvailable(processObj)
        return (completeOrNot, listOfMissingStuff)
    
    ####################################################################################
    def cloneServiceDetails(self, existingContent:dict, newProcess) -> dict:
        """
        Clone content of the service

        :param existingContent: What the process currently holds about the service
        :type existingContent: dict
        :param newProcess: The new process as object
        :type newProcess: Process|ProcessInterface
        :return: The copy of the service details
        :rtype: dict
        
        """
        return AS_cloneServiceDetails(existingContent, newProcess)
    
    ##################################################
    def calculatePriceForService(self, process, additionalArguments:dict, transferObject:object) -> dict:
        """
        Calculate the price for all content of the service
        
        :param process: The process with all its details
        :type process: ProcessInterface|Process
        :param additionalArguments: Various parameters, differs for every service
        :type additionalArguments: dict
        :param transferObject: Object to transfer data between services
        :type transferObject: object
        :return: Dictionary with all pricing details
        :rtype: dict

        """
        return {}

    ###################################################
    def getFilteredContractors(self, processObj:ProcessInterface|Process) -> tuple[list, object]:
        """
        Get a list of contractors that are available for this service

        :param processObj: The process in question
        :type processObj: ProcessInterface|Process
        :return: List of suitable contractors and a transfer object with additional information, can be used for example to calculate a price based on prior calculations
        :rtype: tuple[list, object]

        """
        # filter by choice of material, post-processings, build plate, etc...
        
        filteredContractors = Filter()

        outList = filteredContractors.getFilteredContractors(processObj)
        
        # return outList, filteredContractors
        return [], {}

Semper.serviceManager.register(SERVICE_NAME, SERVICE_NUMBER, AfterSales())