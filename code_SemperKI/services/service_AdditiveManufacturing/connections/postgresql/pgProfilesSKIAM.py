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
from ...definitions import OrganizationDetailsAM

from logging import getLogger
logger = getLogger("errors")

####################################################################################
def updateUserDetailsSemperKIAM(userHashID:str, session):
    """
    Look for user, update details according to AM specific fields

    :param userHashID: The ID transmitted via signal
    :type userHashID: str
    :return: Nothing
    :rtype: None
    """
    pass

####################################################################################
def updateOrgaDetailsSemperKIAM(orgaHashID:str):
    """
    Look for orga, update details according to AM specific fields

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
        locale = "de-DE"
        if OrganizationDetails.locale in orga.details:
            locale = orga.details[OrganizationDetails.locale]

        # Add details, take from translation file
        # Structure: {ServiceSpecificFields.key: <key>, ServiceSpecificFields.name: "Field_Name", ServiceSpecificFields.unit: <unit>, ServiceSpecificFields.value: Value}
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.powerCosts, ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.powerCosts]), ServiceSpecificFields.unit: UnitsForPriceCalculation.euroPerkWh, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.margin,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.margin]) , ServiceSpecificFields.unit: UnitsForPriceCalculation.percent, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.personnelCosts,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.personnelCosts]), ServiceSpecificFields.unit: UnitsForPriceCalculation.euroPerHour, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.costRatePersonnelEngineering,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.costRatePersonnelEngineering]), ServiceSpecificFields.unit: UnitsForPriceCalculation.euroPerHour, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.repairCosts,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.repairCosts]), ServiceSpecificFields.unit: UnitsForPriceCalculation.percent, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.personnelPreProcessCosts,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.personnelPreProcessCosts]), ServiceSpecificFields.unit: UnitsForPriceCalculation.euroPerkWh, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.amortizationRate,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.amortizationRate]), ServiceSpecificFields.unit: UnitsForPriceCalculation.euroPerHour, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.additionalFixedCosts,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.additionalFixedCosts]), ServiceSpecificFields.unit: UnitsForPriceCalculation.euro, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.costRateEquipmentEngineering,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.costRateEquipmentEngineering]), ServiceSpecificFields.unit: UnitsForPriceCalculation.euroPerHour, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.fixedCostsEquipmentEngineering,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.fixedCostsEquipmentEngineering]), ServiceSpecificFields.unit: UnitsForPriceCalculation.euroPerkWh, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.safetyGasCosts,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.safetyGasCosts]), ServiceSpecificFields.unit: UnitsForPriceCalculation.euroPerHour, ServiceSpecificFields.value: 0.})
        orga.details[OrganizationDetails.services][SERVICE_NAME].append({ServiceSpecificFields.key: OrganizationDetailsAM.roomCosts,ServiceSpecificFields.name: manageTranslations.getTranslation(locale, ["service",SERVICE_NAME,OrganizationDetailsAM.roomCosts]), ServiceSpecificFields.unit: UnitsForPriceCalculation.euroPerHourPerSquareMeter, ServiceSpecificFields.value: 0.})

        orga.save()
    except Exception as e:
        logger.error(f"Error in updateOrgaDetailsSemperKIAM: {str(e)}")