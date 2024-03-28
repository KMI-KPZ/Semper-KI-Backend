"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.serviceManager as Semper

from .connections.postgresql.pgService import updateServiceDetails as CM_updateServiceDetails, deleteServiceDetails as CM_deleteServiceDetails, serviceReady as CM_serviceReady

###################################################
class CreateModel(Semper.ServiceBase):
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

        return CM_updateServiceDetails(existingContent, newContent)
    
    ###################################################
    def deleteServiceDetails(self, existingContent, newContent):
        """
        Run service specific update of service details

        """

        return CM_deleteServiceDetails(existingContent, newContent)
    
    ###################################################
    def serviceReady(self, existingContent) -> bool:
        return CM_serviceReady(existingContent)
    

Semper.serviceManager.register("CREATE_MODEL", 2, CreateModel())