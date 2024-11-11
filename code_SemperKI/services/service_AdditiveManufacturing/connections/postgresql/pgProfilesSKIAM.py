"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Connector to the profiles of the Generic Backend which adds stuff to the details specific to this service
"""

import copy

from Generic_Backend.code_General.definitions import OrganizationDetails, UserDetails, UserNotificationTargets, OrganizationNotificationTargets, SessionContent, ProfileClasses
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists

from logging import getLogger
logger = getLogger("errors")

####################################################################################
def updateUserDetailsSemperKI(userHashID:str, session):
    """
    Look for user, update details according to AM specific fields

    :param userHashID: The ID transmitted via signal
    :type userHashID: str
    :return: Nothing
    :rtype: None
    """

####################################################################################
def updateOrgaDetailsSemperKI(orgaHashID:str):
    """
    Look for orga, update details according to AM specific fields

    :param orgaHashID: The ID transmitted via signal
    :type orgaHashID: str
    :return: Nothing
    :rtype: None
    """