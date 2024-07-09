"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Service specific connections to the database
"""

from ...definitions import ServiceDetails
import logging
logger = logging.getLogger("django_debug")

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
    # TODO
    return existingContent

####################################################################################
def deleteServiceDetails(existingContent, deletedContent):
    """
    Update the content of the current service in the process

    :param existingContent: What the process currently holds about the service
    :type existingContent: Dict
    :param deletedContent: What the user wants deleted
    :type deletedContent: Dict
    :return: New service Instance
    :rtype: Dict
    """
    # TODO
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
    # TODO
    return True

####################################################################################
def cloneServiceDetails(existingContent:dict, newProcess) -> dict:
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
    return existingContent