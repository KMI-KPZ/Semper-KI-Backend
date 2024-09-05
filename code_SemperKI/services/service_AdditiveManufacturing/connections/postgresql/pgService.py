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
            if entry == ServiceDetails.models:
                if existingContent == {} or ServiceDetails.models not in existingContent:
                    existingContent[ServiceDetails.models] = {}
                for fileID in newContent[ServiceDetails.models]:    
                    existingContent[ServiceDetails.models][fileID] = newContent[entry][fileID]
            elif entry == ServiceDetails.materials:
                #if existingContent == {} or ServiceDetails.materials not in existingContent:
                existingContent[ServiceDetails.materials] = {}
                for materialID in newContent[ServiceDetails.materials]:
                    existingContent[ServiceDetails.materials][materialID] = newContent[entry][materialID]
            elif entry == ServiceDetails.postProcessings:
                #if existingContent == {} or ServiceDetails.postProcessings not in existingContent:
                existingContent[ServiceDetails.postProcessings] = {}
                for postProcessingID in newContent[ServiceDetails.postProcessings]:
                    existingContent[ServiceDetails.postProcessings][postProcessingID] = newContent[entry][postProcessingID]
            elif entry == ServiceDetails.calculations:
                if existingContent == {} or ServiceDetails.calculations not in existingContent:
                    existingContent[ServiceDetails.calculations] = {}
                for fileID in newContent[ServiceDetails.calculations]:
                    existingContent[ServiceDetails.calculations][fileID] = newContent[entry][fileID]
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
            if entry == ServiceDetails.models:
                for fileID in deletedContent[ServiceDetails.models]:
                    del existingContent[ServiceDetails.models][fileID]
                if ServiceDetails.calculations in existingContent:
                    del existingContent[ServiceDetails.calculations][fileID] # invalidate calculations since the model doesn't exist anymore
            elif entry == ServiceDetails.materials:
                for materialID in deletedContent[ServiceDetails.materials]:
                    del existingContent[ServiceDetails.materials][materialID]
            elif entry == ServiceDetails.postProcessings:
                for postProcessingsID in deletedContent[ServiceDetails.postProcessings]:
                    del existingContent[ServiceDetails.postProcessings][postProcessingsID]
            elif entry == ServiceDetails.calculations:
                for fileID in deletedContent[ServiceDetails.calculations]:
                    del existingContent[ServiceDetails.calculations][fileID]
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
            if entry == ServiceDetails.models:
                if len(existingContent[ServiceDetails.models]) > 0:
                    checks += 1
            elif entry == ServiceDetails.materials:
                if len(existingContent[ServiceDetails.materials]) > 0:
                    checks += 1
            elif entry == ServiceDetails.postProcessings:
                if len(existingContent[ServiceDetails.postProcessings]) > 0:
                    checks += 0 # optional
            else:
                continue
            
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

        # create new model file but with the content of the old one (except path and such), also carry calculations over
        if ServiceDetails.models in existingContent:
            outDict[ServiceDetails.models] = {}
            if ServiceDetails.calculations in existingContent:
                outDict[ServiceDetails.calculations] = {}
            oldModels = existingContent[ServiceDetails.models]
            for fileKey in newProcess.files:
                if fileKey in oldModels:
                    outDict[ServiceDetails.models][fileKey] = newProcess.files[fileKey]
                    if fileKey in existingContent[ServiceDetails.calculations]:
                        outDict[ServiceDetails.calculations][fileKey] = existingContent[ServiceDetails.calculations][fileKey]
        
        # the rest can just be copied over
        if ServiceDetails.materials in existingContent:
            outDict[ServiceDetails.materials] = existingContent[ServiceDetails.materials]
        if ServiceDetails.postProcessings in existingContent:
            outDict[ServiceDetails.postProcessings] = existingContent[ServiceDetails.postProcessings]
    
    except Exception as error:
        logger.error(f'Generic error in cloneServiceDetails(3D Print): {str(error)}')
    
    return outDict

    