"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Metaclass that handles the services
"""
import enum

from code_General.utilities.customStrEnum import StrEnumExactylAsDefined

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
class ServiceTypes(StrEnumExactylAsDefined):
    """
    Which services does the platform offer. 
    This must be known here, since enums can't be extended!
    
    """
    NONE = enum.auto()
    ADDITIVE_MANUFACTURING = enum.auto()
    CREATE_MODEL = enum.auto()

###################################################
# Class of Services
class _ServiceTypesConversion():
    """
    Same as above but converts between string representation and integer representation
    
    """
    ######################
    _asInt = {ServiceTypes.NONE: 0, ServiceTypes.ADDITIVE_MANUFACTURING: 1, ServiceTypes.CREATE_MODEL: 2}
    _asStr = [ServiceTypes.NONE, ServiceTypes.ADDITIVE_MANUFACTURING, ServiceTypes.CREATE_MODEL]

    ######################
    def toInt(self, serviceName:str) -> int:
        """
        Convert the service name to its integer representation

        :param serviceName: Name of the service as given in ServiceTypes
        :type serviceName: Str
        :return: Integer Code of that service
        :rtype: Int
        """
        return self._asInt[serviceName]
    
    ######################
    def toStr(self, index:int) -> str:
        """
        Convert the service name to its string representation

        :param serviceName: Int code of the service
        :type serviceName: int
        :return: Str Code of that service as given in ServiceTypes
        :rtype: Str
        """
        return self._asStr[index]
    
    ######################
    def getServices(self) -> dict:
        """
        Get all defined services of this plattform

        :return: Dict of Services
        :rtype: dict in JSON Format

        """
        return self._asInt

    
###################################################
translateServiceType = _ServiceTypesConversion()

######################################################
class _ServicesManager():
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

        self._services[name] = serviceClass()

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
serviceManager = _ServicesManager()