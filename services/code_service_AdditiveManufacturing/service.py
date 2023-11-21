"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.services as Semper

from .connections.postgresql.pgService import updateServiceDetails as AM_updateServiceDetails, deleteServiceDetails as AM_deleteServiceDetails

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

Semper.serviceManager.register(Semper.ServiceTypes.ADDITIVE_MANUFACTURING, AdditiveManufacturing)