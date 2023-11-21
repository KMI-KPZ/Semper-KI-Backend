"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Metaclass that handles the services
"""
import enum

from abc import ABC, abstractmethod

###################################################
class ServiceBase(ABC):
    """
    Abstract base class defining the interface that every service has to implement

    """

    ##############################################################
    # Handlers



    ##############################################################
    # Connections

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
    Which services does the platform offer. 
    This must be known here, since enums can't be extended!
    
    """
    ADDITIVE_MANUFACTURING = enum.auto()
    CREATE_MODEL = enum.auto()

######################################################
class ServicesManager():
    """
    The class handling the services

    """

    ####################################################################################
    @property
    def getService(self, savedService : str) -> ServiceBase:
        """
        Depending on the service, select the correct Service class

        :param savedService: The selected service saved in the database as named in ServiceTypes
        :type savedService: str
        :return: The respective Service class
        :rtype: Derived class of ServiceBase
        """

        return self._services[savedService]


    ###################################################
    def __init__(self) -> None:
        self._services = {} # To be filled with the other classes 

    ###################################################
    def register(self, name, serviceClass, **kwargs):
        """
        Registers a new service class
        
        :param name: The name of the service as given in ServiceTypes
        :type name: str
        :param serviceClass: The service class 
        :type serviceClass: Derived Class Instances of ServiceBase
        :param kwargs: Parameters for service class
        :type kwargs: Any
        """

        self._services[name] = serviceClass(kwargs)

    ###################################################
    # def __getattr__(self, name):
    #     """
    #     Call the service Instance

    #     :param name: The name of the service as given in ServiceTypes
    #     :type name: str
    #     """
    #     try:
    #         return object.__getattribute__(self, name)
    #     except AttributeError:
    #         if name in self._services:
    #             return self._services[name]
    #         raise AttributeError(f'No such service: {name}')

###################################################
serviceManager = ServicesManager()