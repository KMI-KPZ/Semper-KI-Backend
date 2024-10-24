"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.serviceManager as Semper

from .connections.postgresql.pgService import updateServiceDetails as P_updateServiceDetails, deleteServiceDetails as P_deleteServiceDetails, serviceReady as P_serviceReady, cloneServiceDetails as P_cloneServiceDetails
from .handlers.checkService import checkIfSelectionIsAvailable as P_checkIfSelectionIsAvailable

###################################################
class Packaging(Semper.ServiceBase):
    """
    All connections of this service that Semper-KI should know about
    
    """
    ###################################################
    def __init__(self) -> None:
        super().__init__()

    ###################################################
    def updateServiceDetails(self, existingContent, newContent):
        """
        Run service specific update of service details

        """

        return P_updateServiceDetails(existingContent, newContent)
    
    ###################################################
    def deleteServiceDetails(self, existingContent, newContent):
        """
        Run service specific update of service details

        """

        return P_deleteServiceDetails(existingContent, newContent)
    
    ###################################################
    def serviceReady(self, existingContent) -> tuple[bool, list[str]]:
        """
        Checks, if service is completely defined
        
        """
        return P_serviceReady(existingContent)
    
    ###################################################
    def checkIfSelectionIsAvailable(self, processObj) -> bool:
        """
        Checks, if the selection of the service is available (material, ...)
        
        """
        return P_checkIfSelectionIsAvailable(processObj)
    
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
        return P_cloneServiceDetails(existingContent, newProcess)

    ###################################################
    def getFilteredContractors(self, processObj) -> list:
        """
        Get a list of contractors that can do the job

        """
        return []

SERVICE_NAME = "PACKAGING"
SERVICE_NUMBER = 5

Semper.serviceManager.register(SERVICE_NAME, SERVICE_NUMBER, Packaging())