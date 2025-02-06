"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Connector to Generic Backend's profile database (User/Organization)
"""

import copy
import asyncio

from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderServiceError

from ....definitions import *
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists

from logging import getLogger
logger = getLogger("errors")

####################################################################################
def userCreatedSemperKI(userHashID:str, session):
    """
    Look for (new) user, update details according to Semper-KI specific fields

    :param userHashID: The ID transmitted via signal
    :type userHashID: str
    :param session: The session object
    :type session: Session
    :return: Nothing
    :rtype: None
    """
    try:
        user, _ = ProfileManagementBase.getUserViaHash(userHashID)
        existingDetails = copy.deepcopy(user.details)

        if UserDetails.notificationSettings in existingDetails:
            existingDetails = existingDetails[UserDetails.notificationSettings]
            if ProfileClasses.user in existingDetails:
                existingDetails = existingDetails[ProfileClasses.user]
            else:
                user.details[UserDetails.notificationSettings][ProfileClasses.user] = {}
        else:
            user.details[UserDetails.notificationSettings] = {}
            user.details[UserDetails.notificationSettings][ProfileClasses.user] = {}
        
        for entry in NotificationSettingsUserSemperKI:
            setting = entry.value
            if setting in existingDetails:
                user.details[UserDetails.notificationSettings][ProfileClasses.user][setting] = {}
                if UserNotificationTargets.email in existingDetails[setting]:
                    user.details[UserDetails.notificationSettings][ProfileClasses.user][setting][UserNotificationTargets.email] = existingDetails[setting][UserNotificationTargets.email]
                else:
                    user.details[UserDetails.notificationSettings][ProfileClasses.user][setting][UserNotificationTargets.email] = True
                if UserNotificationTargets.event in existingDetails[setting]:
                    user.details[UserDetails.notificationSettings][ProfileClasses.user][setting][UserNotificationTargets.event] = existingDetails[setting][UserNotificationTargets.event]
                else:
                    user.details[UserDetails.notificationSettings][ProfileClasses.user][setting][UserNotificationTargets.event] = True
            else:
                user.details[UserDetails.notificationSettings][ProfileClasses.user][setting] = {UserNotificationTargets.email: True, UserNotificationTargets.event: True}

        if session[SessionContent.IS_PART_OF_ORGANIZATION]:
            existingDetails = copy.deepcopy(user.details)
            if OrganizationDetails.notificationSettings in existingDetails:
                existingDetails = existingDetails[OrganizationDetails.notificationSettings]
                if ProfileClasses.organization in existingDetails:
                    existingDetails = existingDetails[ProfileClasses.organization]
                else:
                    user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization] = {}
            else:
                user.details[OrganizationDetails.notificationSettings] = {}
                user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization] = {}
            
            for permission in session[SessionContent.USER_PERMISSIONS]:
                listOfPermittedNotifications = MapPermissionsToOrgaNotifications.permissionsToNotifications[permission]
                for setting in listOfPermittedNotifications:
                    if setting in existingDetails:
                        user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting] = {}
                        if OrganizationNotificationTargets.email in existingDetails[setting]:
                            user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.email] = existingDetails[setting][OrganizationNotificationTargets.email]
                        else:
                            user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.email] = True
                        if OrganizationNotificationTargets.event in existingDetails[setting]:
                            user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.event] = existingDetails[setting][OrganizationNotificationTargets.event]
                        else:
                            user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.event] = True
                    else:
                        user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting] = {OrganizationNotificationTargets.email: True, OrganizationNotificationTargets.event: True}

        user.save()
    except Exception as error:
        logger.error(f'Could not create user details in SemperKI: {str(error)}')
        return None

####################################################################################
async def fetchCoordinates(address):
    try:
        # https://nominatim.org/release-docs/develop/api/Search/
        addressDictForLookup = {
            "city" : address[Addresses.city],
            "street" : address[Addresses.street] + " " + str(address[Addresses.houseNumber]),
            "country" : address[Addresses.country],
            "postalcode" : address[Addresses.zipcode]
        }
        async with Nominatim(user_agent="geo_distance_calculator", adapter_factory=AioHTTPAdapter) as geolocator:
            for attempt in range(3):  # Retry up to 3 times
                try:
                    location = await geolocator.geocode(addressDictForLookup, exactly_one=True, timeout=10)
                    if location is None:
                        raise ValueError("Location not found.")
                    return (location.latitude, location.longitude)
                except GeocoderServiceError:
                    if attempt == 2:  # Last attempt
                        return None
                except Exception:
                    return None
            return None
    except Exception as e:
        return e

####################################################################################
def userUpdatedSemperKI(userHashID:str, session, updates):
    """
    Update user details according to Semper-KI specific fields
    
    :param userHashID: The ID transmitted via signal
    :type userHashID: str
    :param session: The session object
    :type session: Session
    :return: Nothing
    :rtype: None

    """
    try:
        user, _ = ProfileManagementBase.getUserViaHash(userHashID)
        existingDetails = copy.deepcopy(user.details)

        if UserUpdateType.address in updates:
            if UserDetails.addresses in existingDetails:
                for addressID, address in existingDetails[UserDetails.addresses].items():
                    coordsOfAddress = asyncio.run(fetchCoordinates(address))
                    if coordsOfAddress is not None:
                        user.details[UserDetails.addresses][addressID][AddressesSKI.coordinates] = coordsOfAddress
                    else:
                        user.details[UserDetails.addresses][addressID][AddressesSKI.coordinates] = (0,0)
        user.save()
        return None
    except Exception as error:
        logger.error(f'Could not update user details in SemperKI: {str(error)}')
        return None

####################################################################################
def orgaCreatedSemperKI(orgaHashID:str):
    """
    Look for orga, update details according to Semper-KI specific fields

    :param orgaHashID: The ID transmitted via signal
    :type orgaHashID: str
    :return: Nothing
    :rtype: None
    """
    try:
        orga, _ = ProfileManagementBase.getUserViaHash(orgaHashID)
        existingDetails = copy.deepcopy(orga.details)

        if OrganizationDetails.notificationSettings in existingDetails:
            existingDetails = existingDetails[OrganizationDetails.notificationSettings]
            if ProfileClasses.organization in existingDetails:
                existingDetails = existingDetails[ProfileClasses.organization]
            else:
                orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization] = {}
        else:
            orga.details[OrganizationDetails.notificationSettings] = {}
            orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization] = {}
        
        for entry in NotificationSettingsOrgaSemperKI:
            setting = entry.value
            if setting in existingDetails:
                orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting] = {}
                if OrganizationNotificationTargets.email in existingDetails[setting]:
                    orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.email] = existingDetails[setting][OrganizationNotificationTargets.email]
                else:
                    orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.email] = True
                if OrganizationNotificationTargets.event in existingDetails[setting]:
                    orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.event] = existingDetails[setting][OrganizationNotificationTargets.event]
                else:
                    orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.event] = True
            else:
                orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting] = {OrganizationNotificationTargets.email: True, OrganizationNotificationTargets.event: True}

        existingDetails = copy.deepcopy(orga.details)
        for entry in PrioritiesForOrganizationSemperKI:
            setting = entry.value
            if setting in existingDetails[OrganizationDetails.priorities]:
                orga.details[OrganizationDetails.priorities][setting] = {}
                if PriorityTargetsSemperKI.value in existingDetails[OrganizationDetails.priorities][setting]:
                    orga.details[OrganizationDetails.priorities][setting][PriorityTargetsSemperKI.value] = existingDetails[OrganizationDetails.priorities][setting][PriorityTargetsSemperKI.value]
                else:
                    orga.details[OrganizationDetails.priorities][setting][PriorityTargetsSemperKI.value] = 4
            else:
                orga.details[OrganizationDetails.priorities][setting] = {PriorityTargetsSemperKI.value: 4}

        if OrganizationDetailsSKI.maturityLevel not in existingDetails:
            orga.details[OrganizationDetailsSKI.maturityLevel] = 0
        else:
            orga.details[OrganizationDetailsSKI.maturityLevel] = existingDetails[OrganizationDetailsSKI.maturityLevel]
        
        if OrganizationDetailsSKI.resilienceScore not in existingDetails:
            orga.details[OrganizationDetailsSKI.resilienceScore] = 0
        else:
            orga.details[OrganizationDetailsSKI.resilienceScore] = existingDetails[OrganizationDetailsSKI.resilienceScore]

        orga.save()
    except Exception as error:
        logger.error(f'Could not update orga details in SemperKI: {str(error)}')
        return None
    
####################################################################################
def orgaUpdatedSemperKI(orgaHashID:str, session, updates):
    """
    Update orga details according to Semper-KI specific fields
    
    :param userHashID: The ID transmitted via signal
    :type userHashID: str
    :param session: The session object
    :type session: Session
    :return: Nothing
    :rtype: None

    """
    try:
        orga = ProfileManagementBase.getOrganizationObject(hashID=orgaHashID)
        if isinstance(orga, Exception):
            raise orga
        existingDetails = copy.deepcopy(orga.details)
        if OrganizationUpdateType.address in updates:
            if OrganizationDetails.addresses in existingDetails:
                for addressID, address in existingDetails[OrganizationDetails.addresses].items():
                    coordsOfAddress = asyncio.run(fetchCoordinates(address))
                    if coordsOfAddress is not None:
                        orga.details[OrganizationDetails.addresses][addressID][AddressesSKI.coordinates] = coordsOfAddress
                    else:
                        orga.details[OrganizationDetails.addresses][addressID][AddressesSKI.coordinates] = (0,0)
        
        orga.save()
        return None
    except Exception as error:
        logger.error(f'Could not update orga details in SemperKI: {str(error)}')
        return None

####################################################################################
def gatherUserHashIDsAndNotificationPreference(orgaOrUserID:str, notification:str, notificationType:str):
    """
    Gather all IDs for either a user or members of an organization and their preference for a certain notification

    :param orgaOrUserID: The hashed ID of the user/orga in question
    :type orgaOrUserID: str
    :param notification: The notification sent
    :type notification: str
    :param notificationType: What kind of notification it is (email or event)
    :type notificationType: str
    :return: dict with userID(s) and their to get the notification or not
    :rtype: dict
    
    """
    try:
        if ProfileManagementBase.checkIfHashIDBelongsToOrganization(orgaOrUserID):
            # Gather all users who are in that organization and their preference
            organizationObj = ProfileManagementBase.getOrganizationObject(hashID=orgaOrUserID)
            if isinstance(organizationObj, Exception):
                raise organizationObj
            resultDict = {}
            for user in organizationObj.users.all():
                hashedIDOfUser = user.hashedID
                if checkIfNestedKeyExists(user.details, UserDetails.notificationSettings, ProfileClasses.organization):
                    preferencesOfUserAsPartOfOrga = user.details[UserDetails.notificationSettings][ProfileClasses.organization]
                    if notification in preferencesOfUserAsPartOfOrga and preferencesOfUserAsPartOfOrga[notification][notificationType]:
                        resultDict[hashedIDOfUser] = True
                    else:
                        resultDict[hashedIDOfUser] = False
                else:
                    resultDict[hashedIDOfUser] = True
            return resultDict
        else:
            preferencesOfUser = ProfileManagementBase.getNotificationPreferences(orgaOrUserID)
            if preferencesOfUser is None:
                raise Exception("Error in getting user preferences")
            if notification in preferencesOfUser and preferencesOfUser[notification][notificationType]:
                return {orgaOrUserID: True}
            else:
                return {orgaOrUserID: False}
    except Exception as error:
        logger.error(f'could not gather notification settings: {str(error)}')
        return error
    
