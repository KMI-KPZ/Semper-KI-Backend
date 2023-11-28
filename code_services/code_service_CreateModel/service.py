"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.services as Semper

from .connections.postgresql.pgService import updateServiceDetails as CM_updateServiceDetails, deleteServiceDetails as CM_deleteServiceDetails

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
    

Semper.serviceManager.register("CREATE_MODEL", 2, CreateModel())