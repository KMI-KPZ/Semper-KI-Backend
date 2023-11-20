"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.services as Semper

from .connections.postgresql.pgService import updateServiceDetails

###################################################
class AdditiveManufacturing_Handler(Semper.Services_Handler):
    """
    All handlers of this service

    """
    ###################################################
    def __init__(self) -> None:
        super().__init__()

###################################################
class AdditiveManufacturing_Connections(Semper.Services_Connections):
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

        return updateServiceDetails(existingContent, newContent)
    

Semper.services[Semper.ServiceTypes.ADDITIVE_MANUFACTURING] = {Semper.ServicesDictionaryStructure.HANDLER: AdditiveManufacturing_Handler(), Semper.ServicesDictionaryStructure.CONNECTIONS: AdditiveManufacturing_Connections()}