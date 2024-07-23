"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Connector to Generic Backend's profile database (User/Organization)
"""

import copy

from ....definitions import NotificationSettingsOrgaSemperKI, NotificationSettingsUserSemperKI, PrioritiesForOrganizationSemperKI, PriorityTargetsSemperKI, MapPermissionsToOrgaNotifications
from Generic_Backend.code_General.definitions import OrganizationDetails, UserDetails, UserNotificationTargets, OrganizationNotificationTargets, SessionContent, ProfileClasses
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase

from logging import getLogger
logger = getLogger("errors")

####################################################################################
def updateUserDetailsSemperKI(userHashID:str, session):
    """
    Look for user, update details according to Semper-KI specific fields

    :param userHashID: The ID transmitted via signal
    :type userHashID: str
    :return: Nothing
    :rtype: None
    """
    try:
        user, _ = ProfileManagementBase.getUserViaHash(userHashID)
        existingDetails = copy.deepcopy(user.details)

        for entry in NotificationSettingsUserSemperKI:
            setting = entry.value
            if setting in existingDetails[UserDetails.notificationSettings]:
                user.details[UserDetails.notificationSettings][ProfileClasses.user][setting] = {}
                if UserNotificationTargets.email in existingDetails[UserDetails.notificationSettings][ProfileClasses.user][setting]:
                    user.details[UserDetails.notificationSettings][ProfileClasses.user][setting][UserNotificationTargets.email] = existingDetails[UserDetails.notificationSettings][ProfileClasses.user][setting][UserNotificationTargets.email]
                else:
                    user.details[UserDetails.notificationSettings][ProfileClasses.user][setting][UserNotificationTargets.email] = True
                if UserNotificationTargets.event in existingDetails[UserDetails.notificationSettings][ProfileClasses.user][setting]:
                    user.details[UserDetails.notificationSettings][ProfileClasses.user][setting][UserNotificationTargets.event] = existingDetails[UserDetails.notificationSettings][ProfileClasses.user][setting][UserNotificationTargets.event]
                else:
                    user.details[UserDetails.notificationSettings][ProfileClasses.user][setting][UserNotificationTargets.event] = True
            else:
                user.details[UserDetails.notificationSettings][ProfileClasses.user][setting] = {UserNotificationTargets.email: True, UserNotificationTargets.event: True}

        if session[SessionContent.IS_PART_OF_ORGANIZATION]:
            for permission in session[SessionContent.USER_PERMISSIONS]:
                listOfPermittedNotifications = MapPermissionsToOrgaNotifications.permissionsToNotifications[permission]
                for setting in listOfPermittedNotifications:
                    if setting in existingDetails[OrganizationDetails.notificationSettings][ProfileClasses.organization]:
                        user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting] = {}
                        if OrganizationNotificationTargets.email in existingDetails[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting]:
                            user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.email] = existingDetails[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.email]
                        else:
                            user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.email] = True
                        if OrganizationNotificationTargets.event in existingDetails[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting]:
                            user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.event] = existingDetails[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.event]
                        else:
                            user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.event] = True
                    else:
                        user.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting] = {OrganizationNotificationTargets.email: True, OrganizationNotificationTargets.event: True}

        user.save()
    except Exception as error:
        logger.error(f'Could not update user details in SemperKI: {str(error)}')
        return None

####################################################################################
def updateOrgaDetailsSemperKI(orgaHashID:str):
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

        for entry in NotificationSettingsOrgaSemperKI:
            setting = entry.value
            if setting in existingDetails[OrganizationDetails.notificationSettings][ProfileClasses.organization]:
                orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting] = {}
                if OrganizationNotificationTargets.email in existingDetails[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting]:
                    orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.email] = existingDetails[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.email]
                else:
                    orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.email] = True
                if OrganizationNotificationTargets.event in existingDetails[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting]:
                    orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.event] = existingDetails[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.event]
                else:
                    orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting][OrganizationNotificationTargets.event] = True
            else:
                orga.details[OrganizationDetails.notificationSettings][ProfileClasses.organization][setting] = {OrganizationNotificationTargets.email: True, OrganizationNotificationTargets.event: True}

        for entry in PrioritiesForOrganizationSemperKI:
            setting = entry.value
            if setting in existingDetails[OrganizationDetails.priorities]:
                orga.details[OrganizationDetails.priorities][setting] = {}
                if PriorityTargetsSemperKI.value in existingDetails[OrganizationDetails.priorities][setting]:
                    orga.details[OrganizationDetails.priorities][setting][PriorityTargetsSemperKI.value] = existingDetails[OrganizationDetails.priorities][setting][PriorityTargetsSemperKI.value]
                else:
                    orga.details[OrganizationDetails.priorities][setting][PriorityTargetsSemperKI.value] = 3
            else:
                orga.details[OrganizationDetails.priorities][setting] = {PriorityTargetsSemperKI.value: 3}

        orga.save()
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
                preferencesOfUserAsPartOfOrga = user.details[UserDetails.notificationSettings][ProfileClasses.organization]
                if notification in preferencesOfUserAsPartOfOrga and preferencesOfUserAsPartOfOrga[notification][notificationType]:
                    resultDict[hashedIDOfUser] = True
                else:
                    resultDict[hashedIDOfUser] = False
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