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
def initializeService(serviceDetails:dict) -> dict:
    """
    Initialize the service
    
    """
    try:
        if ServiceDetails.groups not in serviceDetails:
            serviceDetails[ServiceDetails.groups] = [{ServiceDetails.models: {}, ServiceDetails.material: {}, ServiceDetails.postProcessings: {}, ServiceDetails.color: {}, ServiceDetails.context: ""}]
        return serviceDetails
    except (Exception) as error:
        logger.error(f'Generic error in initializeService(3D Print): {str(error)}')

####################################################################################
def parseServiceDetails(existingContent:dict) -> dict|Exception:
    """
    Display the service content for the Frontend

    :param existingContent: What the process currently holds about the service
    :type existingContent: Dict
    :return: The service content for the frontend
    :rtype: Dict
    
    """
    try:
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
                        case ServiceDetails.color:
                            outEntry[ServiceDetails.color] = existingContent[ServiceDetails.groups][groupIdx][ServiceDetails.color]
                        case ServiceDetails.context:
                            outEntry[ServiceDetails.context] = existingContent[ServiceDetails.groups][groupIdx][ServiceDetails.context]
                outContent[ServiceDetails.groups].append(outEntry)
        return outContent
    except (Exception) as error:
        logger.error(f'Generic error in parseServiceDetails(3D Print): {str(error)}')
        return error

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
        if ServiceDetails.groups not in existingContent:
            existingContent[ServiceDetails.groups] = [{ServiceDetails.models: {}, ServiceDetails.material: {}, ServiceDetails.postProcessings: {}, ServiceDetails.color: {}, ServiceDetails.context: ""}]
        for idx, newContentGroup in enumerate(newContent[ServiceDetails.groups]):
            if idx >= len(existingContent[ServiceDetails.groups]):
                existingContent[ServiceDetails.groups].append({ServiceDetails.models: {}, ServiceDetails.material: {}, ServiceDetails.postProcessings: {}, ServiceDetails.color: {}, ServiceDetails.context: ""})
            existingGroup = existingContent[ServiceDetails.groups][idx]

            for entry in newContentGroup:
                if entry == ServiceDetails.models:
                    if existingGroup == {} or ServiceDetails.models not in existingGroup:
                        existingGroup[ServiceDetails.models] = {}
                    for fileID in newContentGroup[ServiceDetails.models]:
                        existingGroup[ServiceDetails.models][fileID] = newContentGroup[entry][fileID]
                elif entry == ServiceDetails.material:
                    existingGroup[ServiceDetails.material] = newContentGroup[entry]
                elif entry == ServiceDetails.postProcessings:
                    existingGroup[ServiceDetails.postProcessings] = {}
                    for postProcessingID in newContentGroup[ServiceDetails.postProcessings]:
                        existingGroup[ServiceDetails.postProcessings][postProcessingID] = newContentGroup[entry][postProcessingID]
                elif entry == ServiceDetails.calculations:
                    if existingGroup == {} or ServiceDetails.calculations not in existingGroup:
                        existingGroup[ServiceDetails.calculations] = {}
                    for fileID in newContentGroup[ServiceDetails.calculations]:
                        existingGroup[ServiceDetails.calculations][fileID] = newContentGroup[entry][fileID]
                elif entry == ServiceDetails.context:
                    existingGroup[ServiceDetails.context] = newContentGroup[entry]
                elif entry == ServiceDetails.color:
                    existingGroup[ServiceDetails.color] = newContentGroup[entry]
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
        if existingContent == deletedContent:
            existingContent = {}
        groupIdxForExistingContent = 0
        for idx in range(len(deletedContent[ServiceDetails.groups])):
            deletedContentGroup = deletedContent[ServiceDetails.groups][idx]
            if groupIdxForExistingContent >= len(existingContent[ServiceDetails.groups]):
                logger.error("The group to delete does not exist.")
                continue
            existingGroup = existingContent[ServiceDetails.groups][groupIdxForExistingContent]
            if "delete" in deletedContentGroup and deletedContentGroup["delete"] is True:
                del existingContent[ServiceDetails.groups][groupIdxForExistingContent]
                continue
            for entry in deletedContentGroup:
                match entry:
                    case ServiceDetails.models:
                        for fileID in deletedContentGroup[ServiceDetails.models]:
                            del existingGroup[ServiceDetails.models][fileID]
                            if ServiceDetails.calculations in existingGroup and ServiceDetails.calculations not in deletedContentGroup:
                                del existingGroup[ServiceDetails.calculations][fileID] # invalidate calculations since the model doesn't exist anymore
                    case ServiceDetails.material:
                        existingGroup[ServiceDetails.material] = {}
                        if ServiceDetails.color in existingGroup:
                            existingGroup[ServiceDetails.color] = {}
                    case ServiceDetails.postProcessings:
                        for postProcessingsID in deletedContentGroup[ServiceDetails.postProcessings]:
                            del existingGroup[ServiceDetails.postProcessings][postProcessingsID]
                    case ServiceDetails.calculations:
                        for fileID in deletedContentGroup[ServiceDetails.calculations]:
                            del existingGroup[ServiceDetails.calculations][fileID]
                    case ServiceDetails.context:
                        existingGroup[ServiceDetails.context] = ""
                    case ServiceDetails.color:
                        existingGroup[ServiceDetails.color] = {}
                    case _:
                        raise NotImplementedError("This service detail does not exist (yet).")
            groupIdxForExistingContent += 1

    except (Exception) as error:
        logger.error(f'Generic error in updateServiceDetails(3D Print): {str(error)}')
    
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
        for group in existingContent[ServiceDetails.groups]:
            if ServiceDetails.models in group:
                if fileID in group[ServiceDetails.models]:
                    return True
            if ServiceDetails.calculations in group:
                if fileID in group[ServiceDetails.calculations]:
                    return True
        return False
    except (Exception) as error:
        logger.error(f'Generic error in isFileRelevantForService(3D Print): {str(error)}')
        return False

####################################################################################
def serviceReady(existingContent:dict) -> tuple[bool, list[dict]]:
    """
    Check if everything is there

    :param existingContent: What the process currently holds about the service
    :type existingContent: Dict
    :return: Tuple of True if all components are there and a list what's missing
    :rtype: Tuple[bool,list[str]]
    """

    try:
        listOfWhatIsMissing = []
        
        for idx, group in enumerate(existingContent[ServiceDetails.groups]):
            if ServiceDetails.models in group:
                if len(group[ServiceDetails.models]) == 0:
                    listOfWhatIsMissing.append({"groupID": idx, "key": str(ServiceDetails.models)})
            else:
                listOfWhatIsMissing.append({"groupID": idx, "key": str(ServiceDetails.models)})
            
            if ServiceDetails.material in group:
                if len(group[ServiceDetails.material]) == 0:
                    listOfWhatIsMissing.append({"groupID": idx, "key": str(ServiceDetails.material)})
            else:
                listOfWhatIsMissing.append({"groupID": idx, "key": str(ServiceDetails.material)})
            if ServiceDetails.postProcessings in group:
                if len(group[ServiceDetails.postProcessings]) == 0:
                    pass # TODO, current optional
            else:
                pass
            
        return (True, listOfWhatIsMissing) if len(listOfWhatIsMissing) == 0 else (False, listOfWhatIsMissing)
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
        outDict = {ServiceDetails.groups: []}

        # create new model file but with the content of the old one (except path and such), also carry calculations over
        for group in existingContent[ServiceDetails.groups]:
            tempDict = {}
            if ServiceDetails.models in group:
                tempDict[ServiceDetails.models] = {}
                if ServiceDetails.calculations in group:
                    tempDict[ServiceDetails.calculations] = {}
                oldModels = group[ServiceDetails.models]
                for fileKey in newProcess.files:
                    if fileKey in oldModels:
                        tempDict[ServiceDetails.models][fileKey] = newProcess.files[fileKey]
                        if fileKey in group[ServiceDetails.calculations]:
                            tempDict[ServiceDetails.calculations][fileKey] = group[ServiceDetails.calculations][fileKey]
            
            # the rest can just be copied over
            if ServiceDetails.material in group:
                tempDict[ServiceDetails.material] = group[ServiceDetails.material]
            if ServiceDetails.postProcessings in group:
                tempDict[ServiceDetails.postProcessings] = group[ServiceDetails.postProcessings]
            if ServiceDetails.context in group:
                tempDict[ServiceDetails.context] = group[ServiceDetails.context]
            if ServiceDetails.color in group:
                tempDict[ServiceDetails.color] = group[ServiceDetails.color]
            outDict[ServiceDetails.groups].append(tempDict)
    
    except Exception as error:
        logger.error(f'Generic error in cloneServiceDetails(3D Print): {str(error)}')
    
    return outDict

    