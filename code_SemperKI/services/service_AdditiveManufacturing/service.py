"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Class which describes the service in particular
"""
import code_SemperKI.serviceManager as Semper
from code_SemperKI.modelFiles.processModel import ProcessInterface, Process

from .connections.postgresql.pgService import updateServiceDetails as AM_updateServiceDetails, deleteServiceDetails as AM_deleteServiceDetails, serviceReady as AM_serviceIsReady, cloneServiceDetails as AM_cloneServiceDetails
from .handlers.checkService import checkIfSelectionIsAvailable as AM_checkIfSelectionIsAvailable
from .connections.filterViaSparql import *
from .definitions import ServiceDetails

###################################################
class AdditiveManufacturing(Semper.ServiceBase):
    """
    All functions of this service

    """

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
    def serviceReady(self, existingContent) -> bool:
        """
        Checks if the service is completely defined
        
        """
        return AM_serviceIsReady(existingContent)

    ###################################################
    def checkIfSelectionIsAvailable(self, processObj:ProcessInterface|Process) -> bool:
        """
        Checks, if the selection of the service is available (material, ...)
        
        """
        return AM_checkIfSelectionIsAvailable(processObj)
    
    ####################################################################################
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

    ###################################################
    def getFilteredContractors(self, processObj:ProcessInterface|Process) -> list:
        """
        Get a list of contractors that are available for this service

        :param processObj: The process in question
        :type processObj: ProcessInterface|Process
        :return: List of suitable contractors
        :rtype: list

        """
        # filter by choice of material, post-processings, build plate, etc...
        resultListMaterial = []
        if ServiceDetails.materials in processObj.serviceDetails:
            resultListMaterial = filterByMaterial(processObj.serviceDetails[ServiceDetails.materials])

        resultListPostProcess = []
        if ServiceDetails.postProcessings in processObj.serviceDetails:
            resultListPostProcess = filterByPostProcessings(processObj.serviceDetails[ServiceDetails.postProcessings])

        resultListBuildPlate = []
        if ServiceDetails.calculations in processObj.serviceDetails:
            resultListBuildPlate = filterByBuildPlate(processObj.serviceDetails[ServiceDetails.calculations])
        
        return list(set().intersection(resultListMaterial, resultListPostProcess, resultListBuildPlate))

SERVICE_NAME = "ADDITIVE_MANUFACTURING"
SERVICE_NUMBER = 1

Semper.serviceManager.register(SERVICE_NAME, SERVICE_NUMBER, AdditiveManufacturing())