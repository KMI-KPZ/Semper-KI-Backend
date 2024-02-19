"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions specific for 3D printing service that access the database directly
"""

from Generic_Backend.code_General.definitions import FileObjectContent

from ...definitions import ServiceDetails
import logging
logger = logging.getLogger("errors")

####################################################################################
def updateServiceDetails(existingContent, newContent):
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
            else:
                raise NotImplementedError("This service detail does not exist (yet).")

    except (Exception) as error:
        logger.error(f'Generic error in updateServiceDetails(3D Print): {str(error)}')
    
    return existingContent

####################################################################################
def deleteServiceDetails(existingContent, deletedContent):
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
            elif entry == ServiceDetails.material:
                del existingContent[ServiceDetails.material]
            elif entry == ServiceDetails.postProcessings:
                del existingContent[ServiceDetails.postProcessings]
            else:
                raise NotImplementedError("This service detail does not exist (yet).")

    except (Exception) as error:
        logger.error(f'Generic error in updateServiceDetails(3D Print): {str(error)}')
    
    return existingContent

####################################################################################
def serviceReady(existingContent) -> bool:
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
            #elif entry == ServiceDetails.postProcessings and len(existingContent[ServiceDetails.postProcessings]) > 0: # optional
                #checks += 1
            else:
                raise NotImplementedError("This service detail does not exist (yet).")
            
        return True if checks >= 2 else False
    except (Exception) as error:
        logger.error(f'Generic error in serviceReady(3D Print): {str(error)}')
        return False