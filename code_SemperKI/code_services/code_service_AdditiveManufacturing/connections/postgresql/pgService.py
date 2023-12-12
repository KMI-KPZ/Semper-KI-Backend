"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions specific for 3D printing service that access the database directly
"""

from code_General.definitions import FileObject

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
                existingContent[ServiceDetails.model] = {}
            elif entry == ServiceDetails.material:
                existingContent[ServiceDetails.material] = ""
            elif entry == ServiceDetails.postProcessings:
                existingContent[ServiceDetails.postProcessings] = ""
            else:
                raise NotImplementedError("This service detail does not exist (yet).")

    except (Exception) as error:
        logger.error(f'Generic error in updateServiceDetails(3D Print): {str(error)}')
    
    return existingContent

