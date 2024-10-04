"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.serviceManager as Semper

from .connections.postgresql.pgService import updateServiceDetails as QC_updateServiceDetails, deleteServiceDetails as QC_deleteServiceDetails, serviceReady as QC_serviceReady, cloneServiceDetails as QC_cloneServiceDetails
from .handlers.checkService import checkIfSelectionIsAvailable as QC_checkIfSelectionIsAvailable

###################################################
class QualityControl(Semper.ServiceBase):
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

        return QC_updateServiceDetails(existingContent, newContent)
    
    ###################################################
    def deleteServiceDetails(self, existingContent, newContent):
        """
        Run service specific update of service details

        """

        return QC_deleteServiceDetails(existingContent, newContent)
    
    ###################################################
    def serviceReady(self, existingContent) -> bool:
        """
        Checks, if service is completely defined
        
        """
        return QC_serviceReady(existingContent)
    
    ###################################################
    def checkIfSelectionIsAvailable(self, processObj) -> bool:
        """
        Checks, if the selection of the service is available (material, ...)
        
        """
        return QC_checkIfSelectionIsAvailable(processObj)
    
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
        return QC_cloneServiceDetails(existingContent, newProcess)

    ###################################################
    def getFilteredContractors(self, processObj) -> list:
        """
        Get a list of contractors that can do the job

        """
        return []

SERVICE_NAME = "QUALITY_CONTROL"
SERVICE_NUMBER = 6

Semper.serviceManager.register(SERVICE_NAME, SERVICE_NUMBER, QualityControl())