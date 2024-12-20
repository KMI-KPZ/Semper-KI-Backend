"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.serviceManager as Semper

from .connections.postgresql.pgService import updateServiceDetails as A_updateServiceDetails, deleteServiceDetails as A_deleteServiceDetails, serviceReady as A_serviceReady, cloneServiceDetails as A_cloneServiceDetails
from .handlers.checkService import checkIfSelectionIsAvailable as A_checkIfSelectionIsAvailable

###################################################
class Assembly(Semper.ServiceBase):
    """
    All connections of this service that Semper-KI should know about
    
    """
    ###################################################
    def __init__(self) -> None:
        super().__init__()

    ###################################################
    def initializeServiceDetails(self, serviceDetails:dict) -> dict:
        """
        Initialize the service

        """

    ###################################################
    def updateServiceDetails(self, existingContent, newContent):
        """
        Run service specific update of service details

        """

        return A_updateServiceDetails(existingContent, newContent)
    
    ###################################################
    def deleteServiceDetails(self, existingContent, newContent):
        """
        Run service specific update of service details

        """

        return A_deleteServiceDetails(existingContent, newContent)
    
    ###################################################
    def serviceReady(self, existingContent) -> tuple[bool, list[str]]:
        """
        Checks, if service is completely defined
        
        """
        return A_serviceReady(existingContent)
    
    ###################################################
    def checkIfSelectionIsAvailable(self, processObj) -> bool:
        """
        Checks, if the selection of the service is available (material, ...)
        
        """
        return A_checkIfSelectionIsAvailable(processObj)
    
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
        return A_cloneServiceDetails(existingContent, newProcess)
    
    ##################################################
    def calculatePriceForService(self, process, additionalArguments:dict, transferObject:object) -> dict:
        """
        Calculate the price for all content of the service
        
        :param process: The process with all its details
        :type process: ProcessInterface|Process
        :param additionalArguments: Various parameters, differs for every service
        :type additionalArguments: dict
        :param transferObject: Object that is needed to calculate the price
        :type transferObject: object
        :return: Dictionary with all pricing details
        :rtype: dict

        """
        return {}

    ###################################################
    def getFilteredContractors(self, processObj) -> tuple[list, object]:
        """
        Get a list of contractors that can do the job

        """
        return [], {}

SERVICE_NAME = "ASSEMBLY"
SERVICE_NUMBER = 8

Semper.serviceManager.register(SERVICE_NAME, SERVICE_NUMBER, Assembly())