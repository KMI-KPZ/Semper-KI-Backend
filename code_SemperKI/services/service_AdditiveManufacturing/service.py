"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
from django.conf import settings

import code_SemperKI.serviceManager as Semper
from code_SemperKI.modelFiles.processModel import ProcessInterface, Process
from code_SemperKI.definitions import PricesDetails, ValidationSteps, ValidationInformationForFrontend

from .connections.postgresql.pgService import initializeService as AM_initializeService, parseServiceDetails as AM_parseServiceDetails, updateServiceDetails as AM_updateServiceDetails, deleteServiceDetails as AM_deleteServiceDetails, isFileRelevantForService as AM_isFileRelevantForService, serviceReady as AM_serviceIsReady, cloneServiceDetails as AM_cloneServiceDetails
from .logics.checkServiceLogic import checkIfSelectionIsAvailable as AM_checkIfSelectionIsAvailable
from .connections.filterViaSparql import *
from .definitions import SERVICE_NAME, SERVICE_NUMBER, ServiceSpecificDetailsForContractors
from .logics.costsLogic import Costs
from .logics.femAnalysisLogic import startFEMAnalysis

###################################################
class AdditiveManufacturing(Semper.ServiceBase):
    """
    All functions of this service

    """

    ###################################################
    def initializeServiceDetails(self, serviceDetails) -> None:
        """
        Initialize the service
        
        """
        return AM_initializeService(serviceDetails)

    ###################################################
    def updateServiceDetails(self, existingContent, newContent):
        """
        Run service specific update of service details

        """

        return AM_updateServiceDetails(existingContent, newContent)
    
    ###################################################
    def deleteServiceDetails(self, existingContent, deletedContent):
        """
        Delete stuff from a service

        """
        return AM_deleteServiceDetails(existingContent, deletedContent)
    
    ###################################################
    def isFileRelevantForService(self, existingContent, fileID:str) -> bool:
        """
        Check if a file is relevant for the service

        """
        return AM_isFileRelevantForService(existingContent, fileID)
    
    ###################################################
    def parseServiceDetails(self, existingContent) -> dict:
        """
        Parse the service details for Frontend

        """
        outContent = AM_parseServiceDetails(existingContent)
        if isinstance(outContent, Exception):
            return {}
        return outContent
    
    ###################################################
    def serviceReady(self, existingContent) -> tuple[bool, list[str]]:
        """
        Checks if the service is completely defined
        
        """
        completeOrNot, listOfMissingStuff = AM_serviceIsReady(existingContent)
        if completeOrNot is False:
            for idx, entry in enumerate(listOfMissingStuff):
                listOfMissingStuff[idx]["key"] = "Service" + "-" + SERVICE_NAME + "-" + entry["key"]
        
        return (completeOrNot, listOfMissingStuff)

    ###################################################
    def checkIfSelectionIsAvailable(self, processObj:ProcessInterface|Process) -> bool:
        """
        Checks, if the selection of the service is available (material, ...)
        
        """
        return AM_checkIfSelectionIsAvailable(processObj)
    
    ###################################################
    def cloneServiceDetails(self, existingContent:dict, newProcess:ProcessInterface|Process) -> dict:
        """
        Clone content of the service

        :param existingContent: What the process currently holds about the service
        :type existingContent: dict
        :param newProcess: The new process as object
        :type newProcess: Process|ProcessInterface
        :return: The copy of the service details
        :rtype: dict
        
        """
        return AM_cloneServiceDetails(existingContent, newProcess)
    
    ##################################################
    def calculatePriceForService(self, process:ProcessInterface|Process, additionalArguments:dict, transferObject:object) -> dict:
        """
        Calculate the price for all content of the service
        
        :param process: The process with all its details
        :type process: ProcessInterface|Process
        :param additionalArguments: Various parameters, differs for every service
        :type additionalArguments: dict
        :param transferObject: Transfer object with additional information
        :type transferObject: Filter
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
    def getFilteredContractors(self, processObj:ProcessInterface|Process) -> tuple[dict, object]:
        """
        Get a list of contractors that are available for this service

        :param processObj: The process in question
        :type processObj: ProcessInterface|Process
        :return: List of suitable contractors and a transfer object with additional information, can be used for example to calculate a price based on prior calculations
        :rtype: tuple[list, object]

        """
        # filter by choice of material, post-processings, build plate, etc...
        
        filteredContractors = Filter()

        outDict = filteredContractors.getFilteredContractors(processObj)
        if isinstance(outDict, Exception):
            outDict = {}
        
        return outDict, filteredContractors
    
    ###################################################
    def getServiceSpecificContractorDetails(self, existingDetails:dict, contractor:object) -> dict:
        """
        Get the service specific details for a contractor

        """
        existingDetails[ServiceSpecificDetailsForContractors.verified] = contractor[1]
        existingDetails[ServiceSpecificDetailsForContractors.groups] = contractor[2]
        return existingDetails
    
    ###################################################
    def serviceSpecificTasks(self, session, processObj, validationResults:dict) -> dict|Exception:
        """
        Do service specific tasks

        """
        resultDict = startFEMAnalysis(session, processObj)
        if resultDict[ServiceDetails.groups] == []:
            validationResults[ValidationSteps.serviceSpecificTasks]["FEM"] = {ValidationInformationForFrontend.isSuccessful.value: True}
        else:
            validationResults[ValidationSteps.serviceSpecificTasks]["FEM"] = {ValidationInformationForFrontend.isSuccessful.value: False, "groups": resultDict[ServiceDetails.groups]}
        return validationResults


Semper.serviceManager.register(SERVICE_NAME, SERVICE_NUMBER, AdditiveManufacturing(), settings.STATIC_URL+"media/AM.png")