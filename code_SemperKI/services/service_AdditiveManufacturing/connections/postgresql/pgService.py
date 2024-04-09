"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions specific for 3D printing service that access the database directly
"""

from Generic_Backend.code_General.definitions import FileObjectContent
from code_SemperKI.modelFiles.processModel import Process, ProcessInterface

from ...definitions import ServiceDetails
import logging
logger = logging.getLogger("errors")

####################################################################################
def updateServiceDetails(existingContent:dict, newContent:dict) -> dict:
    """
    Update the content of the current service in the process

    :param existingContent: What the process currently holds about the service
    :type existingContent: Dict
    :param newContent: What the user changed
    :type newContent: Dict
    :return: New service Instance
    :rtype: Dict
    """

    try:
        for entry in newContent:
            if entry == ServiceDetails.model:
                existingContent[ServiceDetails.model] = newContent[entry]
            elif entry == ServiceDetails.material:
                existingContent[ServiceDetails.material] = newContent[entry]
            elif entry == ServiceDetails.postProcessings:
                existingContent[ServiceDetails.postProcessings] = newContent[entry]
            elif entry == ServiceDetails.calculations:
                existingContent[ServiceDetails.calculations] = newContent[entry]
            else:
                raise NotImplementedError("This service detail does not exist (yet).")

    except (Exception) as error:
        logger.error(f'Generic error in updateServiceDetails(3D Print): {str(error)}')
    
    return existingContent

####################################################################################
def deleteServiceDetails(existingContent, deletedContent) -> dict:
    """
    Delete stuff from the service

    :param existingContent: What the process currently holds about the service
    :type existingContent: Dict
    :param deletedContent: What the user wants deleted
    :type deletedContent: Dict
    :return: New service Instance
    :rtype: Dict
    """

    try:
        for entry in deletedContent:
            if entry == ServiceDetails.model:
                del existingContent[ServiceDetails.model]
                if ServiceDetails.calculations in existingContent:
                    del existingContent[ServiceDetails.calculations] # invalidate calculations since the model doesn't exist anymore
            elif entry == ServiceDetails.material:
                del existingContent[ServiceDetails.material]
            elif entry == ServiceDetails.postProcessings:
                del existingContent[ServiceDetails.postProcessings]
            elif entry == ServiceDetails.calculations:
                del existingContent[ServiceDetails.calculations]
            else:
                raise NotImplementedError("This service detail does not exist (yet).")

    except (Exception) as error:
        logger.error(f'Generic error in updateServiceDetails(3D Print): {str(error)}')
    
    return existingContent

####################################################################################
def serviceReady(existingContent:dict) -> bool:
    """
    Check if everything is there

    :param existingContent: What the process currently holds about the service
    :type existingContent: Dict
    :return: True if all components are there
    :rtype: Bool
    """

    try:
        checks = 0
        for entry in existingContent:
            if entry == ServiceDetails.model and FileObjectContent.id in existingContent[ServiceDetails.model]:
                checks += 1
            elif entry == ServiceDetails.material and len(existingContent[ServiceDetails.material]) > 0:
                checks += 1
            elif entry == ServiceDetails.postProcessings and len(existingContent[ServiceDetails.postProcessings]) > 0:
                checks += 0 # optional
            else:
                raise NotImplementedError("This service detail does not exist (yet).")
            
        return True if checks >= 2 else False
    except (Exception) as error:
        logger.error(f'Generic error in serviceReady(3D Print): {str(error)}')
        return False
    
####################################################################################
def cloneServiceDetails(existingContent:dict, newProcess:Process|ProcessInterface) -> dict:
    """
    Clone content of the service

    :param existingContent: What the process currently holds about the service
    :type existingContent: dict
    :param newProcess: The new process as object
    :type newProcess: Process|ProcessInterface
    :return: The copy of the service details
    :rtype: dict
    
    """
    try:
        outDict = {}

        # create new model file but with the content of the old one (except path and such)
        outDict[ServiceDetails.model] = {}
        oldModel = existingContent[ServiceDetails.model]
        for fileKey in newProcess.files:
            if fileKey == oldModel[FileObjectContent.id]:
                outDict[ServiceDetails.model] = newProcess.files[fileKey]
                break
        
        # the rest can just be copied over
        outDict[ServiceDetails.material] = existingContent[ServiceDetails.material]
        outDict[ServiceDetails.calculations] = existingContent[ServiceDetails.calculations]
        outDict[ServiceDetails.postProcessings] = existingContent[ServiceDetails.postProcessings]
    
    except Exception as error:
        logger.error(f'Generic error in cloneServiceDetails(3D Print): {str(error)}')
    
    return outDict

    