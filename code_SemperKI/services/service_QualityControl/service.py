"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
from django.conf import settings

import code_SemperKI.serviceManager as Semper
from code_SemperKI.modelFiles.processModel import ProcessInterface, Process
from code_SemperKI.definitions import PricesDetails

from .connections.postgresql.pgService import initializeService as QC_initializeService, updateServiceDetails as QC_updateServiceDetails, deleteServiceDetails as QC_deleteServiceDetails, isFileRelevantForService as QC_isFileRelevantForService, serviceReady as QC_serviceReady, cloneServiceDetails as QC_cloneServiceDetails
from .logics.checkServiceLogic import checkIfSelectionIsAvailable as QC_checkIfSelectionIsAvailable
from .connections.filterViaSparql import *
from .definitions import SERVICE_NAME, SERVICE_NUMBER
from .logics.costs import Costs

###################################################
class QualityControl(Semper.ServiceBase):
    """
    All connections of this service that Semper-KI should know about
    
    """

    ###################################################
    def initializeServiceDetails(self, serviceDetails:dict) -> None:
        """
        Initialize the service

        """
        return QC_initializeService(serviceDetails)

    ###################################################
    def updateServiceDetails(self, existingContent, newContent):
        """
        Run service specific update of service details

        """

        return QC_updateServiceDetails(existingContent, newContent)
    
    ###################################################
    def deleteServiceDetails(self, existingContent, deletedContent):
        """
        Run service specific update of service details

        """

        return QC_deleteServiceDetails(existingContent, deletedContent)
    
    ###################################################
    def isFileRelevantForService(self, existingContent, fileID:str) -> bool:
        """
        Check if a file is relevant for the service

        """
        return QC_isFileRelevantForService(existingContent, fileID)

    ###################################################
    def parseServiceDetails(self, existingContent) -> dict:
        """
        Parse the service details for Frontend

        """
        outContent = {}

        return outContent

    ###################################################
    def serviceReady(self, existingContent) -> tuple[bool, list[str]]:
        """
        Checks, if service is completely defined
        
        """
        completeOrNot, listOfMissingStuff = QC_serviceReady(existingContent)
        return (completeOrNot, listOfMissingStuff)
    
    ###################################################
    def checkIfSelectionIsAvailable(self, processObj) -> bool:
        """
        Checks, if the selection of the service is available (material, ...)
        
        """
        return QC_checkIfSelectionIsAvailable(processObj)

    
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
        return QC_cloneServiceDetails(existingContent, newProcess)
    
    ##################################################
    def calculatePriceForService(self, process, additionalArguments:dict, transferObject:object) -> dict:
        """
        Calculate the price for all content of the service
        
        :param process: The process with all its details
        :type process: ProcessInterface|Process
        :param additionalArguments: Various parameters, differs for every service
        :type additionalArguments: dict
        :param transferObject: Transfer object with additional information
        :type transferObject: object
        :return: Minimum and maximum price
        :rtype: tuple[float, float]

        """
        costsObject = Costs(process, additionalArguments, transferObject)
        costs = costsObject.calculateCosts() 
        outDict = {"groupCosts": []}
        for groupCosts in costs:
            outDict["groupCosts"].append(groupCosts)
            
        # detailed overview, encrypted
        outDict[PricesDetails.details] = costsObject.getEncryptedCostOverview()
        
        return outDict

    ###################################################
    def getFilteredContractors(self, processObj) -> tuple[list, object]:
        """
        Get a list of contractors that can do the job

        :param processObj: The process in question
        :type processObj: ProcessInterface|Process
        :return: List of suitable contractors and a transfer object with additional information, can be used for example to calculate a price based on prior calculations
        :rtype: tuple[list, object]

        """
        filteredContractors = Filter()

        outList = filteredContractors.getFilteredContractors(processObj)
        
        return outList, filteredContractors
    
    ###################################################
    def getServiceSpecificContractorDetails(self, existingDetails:dict, contractor:object) -> dict:
        """
        Get the service specific details for a contractor

        """
        return existingDetails
    
    ###################################################
    def serviceSpecificTasks(self, session, processObj, validationResults:dict) -> dict|Exception:
        """
        Do service specific tasks

        """
        return {}

Semper.serviceManager.register(SERVICE_NAME, SERVICE_NUMBER, QualityControl(), settings.STATIC_URL+"media/QC.png")