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

######################################################
class _ServicesManager():
    """
    The class handling the services

    """

    ###################################################
    class _Structure(StrEnumExactylAsDefined):
        """
        How the services dictionary is structures

        """
        object = enum.auto()
        name = enum.auto()
        identifier = enum.auto()
    
    ###################################################
    def __init__(self) -> None:
        # To be filled with the other classes 
        self._defaultName = "None"
        self._defaultIdx = 0
        self._services = {_ServicesManager._Structure.object: None, _ServicesManager._Structure.name: self._defaultName, _ServicesManager._Structure.identifier: self._defaultIdx} 

    ###################################################
    def register(self, name:str, identifier:int, serviceClassObject):
        """
        Registers a new service class
        
        :param name: The name of the service as given in ServiceTypes
        :type name: str
        :param serviceClass: The service class 
        :type serviceClass: Derived Class Instances of ServiceBase
        :param kwargs: Parameters for service class
        :type kwargs: Any
        """

        self._services[name] = {_ServicesManager._Structure.object: serviceClassObject, _ServicesManager._Structure.name: name, _ServicesManager._Structure.identifier: identifier}

    ###################################################
    def getNone(self) -> int:
        """
        Return default object idx
        
        :return: Idx of none
        :rtype: int
        """
        return self._defaultIdx

    ###################################################
    def getService(self, savedService : str) -> ServiceBase:
        """
        Depending on the service, select the correct Service class

        :param savedService: The selected service saved in the database as named in ServiceTypes
        :type savedService: str
        :return: The respective Service class
        :rtype: Derived class of ServiceBase
        """

        return self._services[savedService][_ServicesManager._Structure.object]

    ####################################################################################
    def getAllServices(self):
        """
        Return all registered services as dict
        
        :return: all registered services as dict
        :rtype: dict
        """
        outDict = dict(self._services)
        for elem in outDict: #remove objects
            outDict[elem].pop(_ServicesManager._Structure.object)

        return outDict


    ######################
    def toInt(self, serviceName:str) -> int:
        """
        Convert the service name to its integer representation

        :param serviceName: Name of the service as given in ServiceTypes
        :type serviceName: Str
        :return: Integer Code of that service
        :rtype: Int
        """
        return self._services[serviceName][_ServicesManager._Structure.identifier]
    
    ######################
    def toStr(self, index:int) -> str:
        """
        Convert the service name to its string representation

        :param serviceName: Int code of the service
        :type serviceName: int
        :return: Str Code of that service as given in ServiceTypes
        :rtype: Str
        """
        outStr = ""
        for elem in self._services:
            if self._services[elem][_ServicesManager._Structure.identifier] == index:
                outStr = self._services[elem][_ServicesManager._Structure.name]
                break

        return outStr

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