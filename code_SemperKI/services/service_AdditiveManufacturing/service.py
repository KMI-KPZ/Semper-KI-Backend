"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.serviceManager as Semper

from .connections.postgresql.pgService import updateServiceDetails as AM_updateServiceDetails, deleteServiceDetails as AM_deleteServiceDetails, serviceReady as AM_serviceIsReady, cloneServiceDetails as AM_cloneServiceDetails
from .handlers.checkService import checkIfSelectionIsAvailable as AM_checkIfSelectionIsAvailable

###################################################
class AdditiveManufacturing(Semper.ServiceBase):
    """
    All functions of this service

    """

    ###################################################
    def updateServiceDetails(self, existingContent, newContent):
        """
        Run service specific update of service details

        """

        return AM_updateServiceDetails(existingContent, newContent)
    
    ###################################################
    def deleteServiceDetails(self, existingContent, deletedContent):
        """
        Delete stuff from a service

        """
        return AM_deleteServiceDetails(existingContent, deletedContent)
    
    ###################################################
    def serviceReady(self, existingContent) -> bool:
        """
        Checks if the service is completely defined
        
        """
        return AM_serviceIsReady(existingContent)

    ###################################################
    def checkIfSelectionIsAvailable(self, processObj) -> bool:
        """
        Checks, if the selection of the service is available (material, ...)
        
        """
        return AM_checkIfSelectionIsAvailable(processObj)
    
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
        return AM_cloneServiceDetails(existingContent, newProcess)

Semper.serviceManager.register("ADDITIVE_MANUFACTURING", 1, AdditiveManufacturing())