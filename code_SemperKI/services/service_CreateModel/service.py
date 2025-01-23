"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.serviceManager as Semper

from .connections.postgresql.pgService import updateServiceDetails as CM_updateServiceDetails, deleteServiceDetails as CM_deleteServiceDetails, serviceReady as CM_serviceReady, cloneServiceDetails as CM_cloneServiceDetails
from .handlers.checkService import checkIfSelectionIsAvailable as CM_checkIfSelectionIsAvailable

###################################################
class CreateModel(Semper.ServiceBase):
    """
    All connections of this service that Semper-KI should know about
    
    """
    ###################################################
    def __init__(self) -> None:
        super().__init__()

    ###################################################
    def initializeServiceDetails(self, serviceDetails:dict) -> dict:
        """
        Initialize the service

        """
        return {}

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
    def isFileRelevantForService(self, existingContent, fileID:str) -> bool:
        """
        Check if a file is relevant for the service

        """
        return False
    
    ###################################################
    def serviceReady(self, existingContent) -> tuple[bool, list[str]]:
        """
        Checks, if service is completely defined
        
        """
        return CM_serviceReady(existingContent)
    
    ###################################################
    def parseServiceDetails(self, existingContent) -> dict:
        """
        Parse the service details for Frontend

        """
        return {}
    
    ###################################################
    def checkIfSelectionIsAvailable(self, processObj) -> bool:
        """
        Checks, if the selection of the service is available (material, ...)
        
        """
        return CM_checkIfSelectionIsAvailable(processObj)

    ##################################################
    def calculatePriceForService(self, process, additionalArguments:dict, transferObject:object) -> dict:
        """
        Calculate the price for all content of the service
        
        :param process: The process with all its details
        :type process: ProcessInterface|Process
        :param additionalArguments: Various parameters, differs for every service
        :type additionalArguments: dict
        :param transferObject: The object that is used to transfer data between the services
        :type transferObject: object
        :return: Dictionary with all pricing details
        :rtype: dict

        """
        return {}
    
    ####################################################################################
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
        return CM_cloneServiceDetails(existingContent, newProcess)

    ###################################################
    def getFilteredContractors(self, processObj) -> tuple[list, object]:
        """
        Get a list of contractors that can do the job

        """
        return [], {}

SERVICE_NAME = "CREATE_MODEL"
SERVICE_NUMBER = 2

Semper.serviceManager.register(SERVICE_NAME, SERVICE_NUMBER, CreateModel())