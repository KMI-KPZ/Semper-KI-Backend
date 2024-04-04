"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.serviceManager as Semper

from .connections.postgresql.pgService import updateServiceDetails as AM_updateServiceDetails, deleteServiceDetails as AM_deleteServiceDetails, serviceReady as AM_serviceIsReady
from .handlers.checkService import checkIfSelectionIsAvailable

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
        return checkIfSelectionIsAvailable(processObj)

Semper.serviceManager.register("ADDITIVE_MANUFACTURING", 1, AdditiveManufacturing())