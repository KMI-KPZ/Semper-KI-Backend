"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Service specific connections to the database
"""

from code_SemperKI.modelFiles.processModel import Process, ProcessInterface
from ...definitions import ServiceDetails

import logging
logger = logging.getLogger("django_debug")

####################################################################################
def initializeService(serviceDetails:dict) -> dict:
    """
    Initialize the service
    
    """
    try:
        return serviceDetails
    except (Exception) as error:
        logger.error(f'Generic error in initializeService(Assembly): {str(error)}')

####################################################################################
def updateServiceDetails(existingContent, newContent) -> dict:
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

        # TODO
        pass

        # if ServiceDetails.groups not in existingContent:
        #     existingContent[ServiceDetails.groups] = [{ServiceDetails.models: {}, ServiceDetails.material: {}, ServiceDetails.postProcessings: {}}]
        # for idx, newContentGroup in enumerate(newContent[ServiceDetails.groups]):
        #     if idx >= len(existingContent[ServiceDetails.groups]):
        #         existingContent[ServiceDetails.groups].append({ServiceDetails.models: {}, ServiceDetails.material: {}, ServiceDetails.postProcessings: {}})
        #     existingGroup = existingContent[ServiceDetails.groups][idx]

        #     for entry in newContentGroup:
        #         if entry == ServiceDetails.models:
        #             if existingGroup == {} or ServiceDetails.models not in existingGroup:
        #                 existingGroup[ServiceDetails.models] = {}
        #             for fileID in newContentGroup[ServiceDetails.models]:
        #                 existingGroup[ServiceDetails.models][fileID] = newContentGroup[entry][fileID]
        #         else:
        #             raise NotImplementedError("This service detail does not exist (yet).")

    except (Exception) as error:
        logger.error(f'Generic error in updateServiceDetails(Assembly): {str(error)}')

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
        if existingContent == deletedContent:
            existingContent = {}
        
        # TODO

    except (Exception) as error:
        logger.error(f'Generic error in updateServiceDetails(Assembly): {str(error)}')
    
    return existingContent

####################################################################################
def isFileRelevantForService(existingContent:dict, fileID:str) -> bool:
    """
    Check if a file is relevant for the service

    :param existingContent: What the process currently holds about the service
    :type existingContent: Dict
    :param fileID: The file ID
    :type fileID: Str
    :return: True if the file is relevant
    :rtype: Bool
    """

    try:

        # TODO

        # for group in existingContent[ServiceDetails.groups]:
        #     if ServiceDetails.calculations in group:
        #         if fileID in group[ServiceDetails.calculations]:
        #             return True
        return False
    except (Exception) as error:
        logger.error(f'Generic error in isFileRelevantForService(Assembly): {str(error)}')
        return False

####################################################################################
def serviceReady(existingContent:dict) -> tuple[bool, list[str]]:
    """
    Check if everything is there

    :param existingContent: What the process currently holds about the service
    :type existingContent: Dict
    :return: True if all components are there
    :rtype: tuple[bool, list[str]]
    """
    try:
        listOfWhatIsMissing = []

        # TODO

        return (True, listOfWhatIsMissing) if len(listOfWhatIsMissing) == 0 else (False, listOfWhatIsMissing)
    except (Exception) as error:
        logger.error(f'Generic error in serviceReady(Assembly): {str(error)}')
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
    # TODO
    try:
        outDict = {}

        # TODO

        # outDict = {ServiceDetails.groups: []}

        # # create new model file but with the content of the old one (except path and such), also carry calculations over
        # for group in existingContent[ServiceDetails.groups]:
        #     tempDict = {}
        #     if ServiceDetails.models in group:
        #         tempDict[ServiceDetails.models] = {}
        #         if ServiceDetails.calculations in group:
        #             tempDict[ServiceDetails.calculations] = {}
        #         oldModels = group[ServiceDetails.models]
        #         for fileKey in newProcess.files:
        #             if fileKey in oldModels:
        #                 tempDict[ServiceDetails.models][fileKey] = newProcess.files[fileKey]
        #                 if fileKey in group[ServiceDetails.calculations]:
        #                     tempDict[ServiceDetails.calculations][fileKey] = group[ServiceDetails.calculations][fileKey]
            
        #     # the rest can just be copied over
        #     if ServiceDetails.material in group:
        #         tempDict[ServiceDetails.material] = group[ServiceDetails.material]
        #     if ServiceDetails.postProcessings in group:
        #         tempDict[ServiceDetails.postProcessings] = group[ServiceDetails.postProcessings]
        #     outDict[ServiceDetails.groups].append(tempDict)
    
    except Exception as error:
        logger.error(f'Generic error in cloneServiceDetails(Assembly): {str(error)}')
    
    return outDict