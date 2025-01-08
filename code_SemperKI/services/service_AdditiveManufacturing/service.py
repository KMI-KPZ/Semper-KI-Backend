"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.serviceManager as Semper
from code_SemperKI.modelFiles.processModel import ProcessInterface, Process
from code_SemperKI.definitions import PricesDetails

from .connections.postgresql.pgService import initializeService as AM_initializeService, updateServiceDetails as AM_updateServiceDetails, deleteServiceDetails as AM_deleteServiceDetails, serviceReady as AM_serviceIsReady, cloneServiceDetails as AM_cloneServiceDetails
from .handlers.public.checkService import checkIfSelectionIsAvailable as AM_checkIfSelectionIsAvailable
from .connections.filterViaSparql import *
from .definitions import SERVICE_NAME, SERVICE_NUMBER
from .logics.costs import Costs

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
    def parseServiceDetails(self, existingContent) -> dict:
        """
        Parse the service details for Frontend

        """
        outContent = {ServiceDetails.groups: []}
        if ServiceDetails.groups in existingContent:
            for groupIdx, group in enumerate(existingContent[ServiceDetails.groups]):
                outEntry = {}
                for serviceDetailType in group:
                    match serviceDetailType:
                        case ServiceDetails.material:
                            outEntry[ServiceDetails.material] = existingContent[ServiceDetails.groups][groupIdx][ServiceDetails.material] # take material object as given
                        case ServiceDetails.postProcessings:
                            outEntry[ServiceDetails.postProcessings] = [existingContent[ServiceDetails.groups][groupIdx][ServiceDetails.postProcessings][content] for content in existingContent[ServiceDetails.groups][groupIdx][ServiceDetails.postProcessings]] # convert postprocessings to list
                        case ServiceDetails.models:
                            outEntry[ServiceDetails.models] = [existingContent[ServiceDetails.groups][groupIdx][ServiceDetails.models][content] for content in existingContent[ServiceDetails.groups][groupIdx][ServiceDetails.models]] # convert models to list
                        case ServiceDetails.calculations:
                            outEntry[ServiceDetails.calculations] = [existingContent[ServiceDetails.groups][groupIdx][ServiceDetails.calculations][content] for content in existingContent[ServiceDetails.groups][groupIdx][ServiceDetails.calculations]] # convert calculations to list
                outContent[ServiceDetails.groups].append(outEntry)
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
        outDict = {}
        for groupIdx, groupCosts in enumerate(costs):
            outDict["group "+str(groupIdx)] = groupCosts
        # detailed overview, encrypted
        outDict[PricesDetails.details] = costsObject.getEncryptedCostOverview()
        return outDict

    ###################################################
    def getFilteredContractors(self, processObj:ProcessInterface|Process) -> tuple[list, object]:
        """
        Get a list of contractors that are available for this service

        :param processObj: The process in question
        :type processObj: ProcessInterface|Process
        :return: List of suitable contractors and a transfer object with additional information, can be used for example to calculate a price based on prior calculations
        :rtype: tuple[list, object]

        """
        # filter by choice of material, post-processings, build plate, etc...
        
        filteredContractors = Filter()

        outList = filteredContractors.getFilteredContractors(processObj)
        
        return outList, filteredContractors


Semper.serviceManager.register(SERVICE_NAME, SERVICE_NUMBER, AdditiveManufacturing())