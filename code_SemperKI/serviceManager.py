"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Metaclass that handles the services

"""
import enum, copy


from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

from abc import ABC, abstractmethod

###################################################
class ServiceBase(ABC):
    """
    Abstract base class defining the interface that every service has to implement

    """

    ##############################################################
    # Handlers

    ###################################################
    @abstractmethod
    def checkIfSelectionIsAvailable(self, processObj) -> bool:
        """
        Checks, if the selection of the service is available (material, ...)
        
        """

    ##############################################################
    # Connections

    ###################################################
    @abstractmethod
    def initializeServiceDetails(self, serviceDetails:dict) -> dict:
        """
        Initialize the service

        """

    ###################################################
    @abstractmethod
    def updateServiceDetails(self, existingContent, newContent):
        """
        Update a service

        """

    ###################################################
    @abstractmethod
    def deleteServiceDetails(self, existingContent, deletedContent):
        """
        Delete stuff from a service

        """

    ###################################################
    @abstractmethod
    def isFileRelevantForService(self, existingContent, fileID:str) -> bool:
        """
        Check if a file is relevant for the service

        """
    
    ###################################################
    @abstractmethod
    def parseServiceDetails(self, existingContent) -> dict:
        """
        Parse the service details for Frontend

        """

    ###################################################
    @abstractmethod
    def serviceReady(self, existingContent) -> tuple[bool, list[str]]:
        """
        Check if a service has been defined completely

        """

    ###################################################
    @abstractmethod
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

    ##################################################
    @abstractmethod
    def calculatePriceForService(self, process, additionalArguments:dict, transferObject:object) -> dict:
        """
        Calculate the price for all content of the service
        
        :param process: The process with all its details
        :type process: ProcessInterface|Process
        :param additionalArguments: Various parameters, differs for every service
        :type additionalArguments: dict
        :param transferObject: Object to transfer data
        :type transferObject: object
        :return: Dictionary with all pricing details
        :rtype: dict
        """

    ###################################################
    @abstractmethod
    def getFilteredContractors(self, processObj) -> tuple[dict, object]:
        """
        Get a list of contractors that can do the job

        """

    ###################################################
    @abstractmethod
    def getServiceSpecificContractorDetails(self, existingDetails:dict, contractor:object) -> dict:
        """
        Get the service specific details for a contractor

        """
    
    ###################################################
    @abstractmethod
    def serviceSpecificTasks(self, session, processObj, validationResults:dict) -> dict|Exception:
        """
        Do service specific tasks

        """

    ###################################################
    @abstractmethod
    def getSearchableDetails(self, existingContent) -> list:
        """
        Get the details for the search index as a string list

        """

###################################################
class ServicesStructure(StrEnumExactlyAsDefined):
    """
    How the services dictionary is structured

    """
    object = enum.auto()
    name = enum.auto()
    identifier = enum.auto()
    imgPath = enum.auto()

######################################################
class _ServicesManager():
    """
    The class handling the services

    """
    
    ###################################################
    def __init__(self) -> None:
        # To be filled with the other classes 
        self._defaultName = "None"
        self._defaultIdx = 0
        self._services = {}
        self._imgPath = ""
        self._services[self._defaultIdx] = {ServicesStructure.object: None, ServicesStructure.name: self._defaultName, ServicesStructure.identifier: self._defaultIdx, ServicesStructure.imgPath: self._imgPath} 

    ###################################################
    def register(self, name:str, identifier:int, serviceClassObject, imgPath:str) -> None:
        """
        Registers a new service class
        
        :param name: The name of the service as given in ServiceTypes
        :type name: str
        :param serviceClass: The service class 
        :type serviceClass: Derived Class Instances of ServiceBase
        :param kwargs: Parameters for service class
        :type kwargs: Any
        """

        self._services[identifier] = {ServicesStructure.object: serviceClassObject, ServicesStructure.name: name, ServicesStructure.identifier: identifier, ServicesStructure.imgPath: imgPath}

    ###################################################
    def getNone(self) -> int:
        """
        Return default object idx
        
        :return: Idx of none
        :rtype: int
        """
        return self._defaultIdx

    ###################################################
    def getService(self, savedService : int) -> ServiceBase:
        """
        Depending on the service, select the correct Service class

        :param savedService: The selected service saved in the dictionary _services
        :type savedService: int
        :return: The respective Service class
        :rtype: Derived class of ServiceBase
        """

        return self._services[savedService][ServicesStructure.object]
    
    ###################################################
    def getImgPath(self, savedService : int) -> str:
        """
        Depending on the service, select the correct Image path

        :param savedService: The selected service saved in the dictionary _services
        :type savedService: int
        :return: The respective Image path
        :rtype: str
        """

        return self._services[savedService][ServicesStructure.imgPath]

    ####################################################################################
    def getAllServices(self) -> list:
        """
        Return all registered services as list
        
        :return: all registered services as list
        :rtype: list
        """
        outDict = copy.deepcopy(self._services)
        for elem in outDict: #remove objects
            outDict[elem].pop(ServicesStructure.object)

        return list(outDict.values())


    ######################
    def toInt(self, serviceName:str) -> int:
        """
        Convert the service name to its integer representation

        :param serviceName: Name of the service as given in ServiceTypes
        :type serviceName: Str
        :return: Integer Code of that service
        :rtype: Int
        """
        outIdx = 0
        for elem in self._services:
            if self._services[elem][ServicesStructure.name] == serviceName:
                outIdx = self._services[elem][ServicesStructure.identifier]
                break
        return outIdx
    
    ######################
    def toStr(self, index:int) -> str:
        """
        Convert the service name to its string representation

        :param serviceName: Int code of the service
        :type serviceName: int
        :return: Str Code of that service as given in ServiceTypes
        :rtype: Str
        """
        return self._services[index][ServicesStructure.name]

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
