"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Connector to the profiles of the Generic Backend which adds stuff to the details specific to this service
"""

import copy

from Generic_Backend.code_General.definitions import OrganizationDetails, UserDetails, UserNotificationTargets, OrganizationNotificationTargets, SessionContent, ProfileClasses
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists

from code_SemperKI.definitions import ServiceSpecificFields, UnitsForPriceCalculation
from code_SemperKI.utilities.locales import manageTranslations

from ...service import SERVICE_NAME
from ...definitions import OrganizationDetailsPP

from logging import getLogger
logger = getLogger("errors")

####################################################################################
def updateUserDetailsSemperKIPP(userHashID:str, session):
    """
    Look for user, update details according to PP specific fields

    :param userHashID: The ID transmitted via signal
    :type userHashID: str
    :return: Nothing
    :rtype: None
    """
    pass

####################################################################################
def updateOrgaDetailsSemperKIPP(orgaHashID:str):
    """
    Look for orga, update details according to PP specific fields

    :param orgaHashID: The ID transmitted via signal
    :type orgaHashID: str
    :return: Nothing
    :rtype: None
    """
    try:
        orga, _ = ProfileManagementBase.getUserViaHash(orgaHashID)

        # Add service specific fields
        if not OrganizationDetails.services in orga.details:
            orga.details[OrganizationDetails.services] = {}
        if not checkIfNestedKeyExists(orga.details, OrganizationDetails.services, SERVICE_NAME):
            orga.details[OrganizationDetails.services][SERVICE_NAME] = []
        else:
            return
        locale = "de-DE"
        if OrganizationDetails.locale in orga.details:
            locale = orga.details[OrganizationDetails.locale]

        # Add details, take from translation file
        # Structure: {ServiceSpecificFields.key: <key>, ServiceSpecificFields.name: "Field_Name", ServiceSpecificFields.unit: <unit>, ServiceSpecificFields.value: Value}
        
        orga.save()
    except Exception as e:
        logger.error(f"Error in updateOrgaDetailsSemperKIPP: {str(e)}")

####################################################################################
def deleteOrgaDetailsSemperKIPP(orgaHashID:str):
    """
    Look for orga, delete details according to PP specific fields

    :param orgaHashID: The ID transmitted via signal
    :type orgaHashID: str
    :return: Nothing
    :rtype: None
    """
    try:
        orga, _ = ProfileManagementBase.getUserViaHash(orgaHashID)

        # Delete service specific field
        del orga.details[OrganizationDetails.services][SERVICE_NAME]

        orga.save()
    except Exception as e:
        logger.error(f"Error in deleteOrgaDetailsSemperKIPP: {str(e)}")