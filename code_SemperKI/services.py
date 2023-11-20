"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Metaclass that handles the services
"""
import enum

from abc import ABC, abstractmethod

###################################################
class Services_Handler(ABC):
    """
    Abstract base class defining the interface that every service has to implement

    """
    ###################################################
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()


###################################################
class Services_Connections(ABC):
    """
    Abstract base class defining the interface that every service has to implement

    """
    ###################################################
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    ###################################################
    @abstractmethod
    def updateServiceDetails(self, existingContent, newContent):
        """
        Update a service

        """
        pass

    ###################################################
    @abstractmethod
    def deleteServiceDetails(self, existingContent, deletedContent):
        """
        Delete stuff from a service

        """
        pass

###################################################
# Enum of Services
class ServiceTypes(enum.StrEnum):
    """
    Which services does the platform offer
    
    """
    ADDITIVE_MANUFACTURING = enum.auto(),
    CREATE_MODEL = enum.auto()

####################################################################################
# A dictionary holding references to the services which is extended in every service definition to be used here

class ServicesDictionaryStructure(enum.StrEnum):
    """
    How should the dictionary be structured?

    """
    HANDLER = enum.auto()
    CONNECTIONS = enum.auto()

services = {ServiceTypes.ADDITIVE_MANUFACTURING: {ServicesDictionaryStructure.HANDLER: "", ServicesDictionaryStructure.CONNECTIONS: ""},
            ServiceTypes.CREATE_MODEL: {ServicesDictionaryStructure.HANDLER: "", ServicesDictionaryStructure.CONNECTIONS: ""}
            }