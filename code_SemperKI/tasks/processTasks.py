"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Tasks that are needed for almost every process 
            and which shall be run in the background
"""
from time import sleep
from django.conf import settings
import logging

from Generic_Backend.code_General.connections.mailer import MailingClass
from Generic_Backend.code_General.connections.postgresql.pgProfiles import profileManagement, ProfileManagementBase, ProfileManagementOrganization, Organization
from Generic_Backend.code_General.definitions import UserNotificationTargets, SessionContent, UserDetails, OrganizationDetails, ProfileClasses, FileObjectContent
from Generic_Backend.code_General.modelFiles.userModel import UserDescription
from Generic_Backend.code_General.utilities.asyncTask import runInBackground

import code_SemperKI.connections.content.postgresql.pgProcesses as DBProcessesAccess
import code_SemperKI.utilities.websocket as websocket
import code_SemperKI.utilities.locales as Locales
import code_SemperKI.handlers.public.files as FileHandler

from ..definitions import ProcessDescription, ProcessUpdates, ProjectDetails, ProcessDetails, NotificationSettingsUserSemperKI, NotificationSettingsOrgaSemperKI
from ..states.stateDescriptions import ProcessStatusAsString, processStatusAsInt
from ..modelFiles.processModel import Process
from ..serviceManager import serviceManager

loggerError = logging.getLogger("errors")


####################################################################
@runInBackground
def sendEMail(userEMailAddress:str, subject:str, toWhom:str, locale:str, message:str):
    """
    Send an E-Mail asynchronously

    :param userEMailAddress: E-Mail address of user
    :type userEMailAddress: str 
    :param subject: What the mail is about
    :type subject: str 
    :param toWhom: User name
    :type toWhom: str 
    :param locale: Language string (e.g. de-DE, en-GB, ...)
    :type locale: str 
    :param message: The actual message
    :type message: str 
    :return: Nothing
    :rtype: None
    
    """
    try:
        if userEMailAddress == None:
            return
        mailer = MailingClass()
        mailer.sendMail(userEMailAddress, subject, mailer.mailingTemplate(toWhom, locale, message) )
    except Exception as error:
        loggerError.error(f"Error while sending email: {str(error)}")

####################################################################
@runInBackground
def verificationOfProcess(processObj:Process, session): # ProcessInterface not needed, verification is database only
    """
    Verify a process' integrity
    
    :param processObj: The process in question
    :type processObj: Process
    :param session: The session of the user who clicked
    :type session: Django Session Object
    :return: Nothing
    :rtype: None

    """
    try:
        valid = True
        # Check if service was correctly defined
        if valid and not serviceManager.getService(processObj.serviceType).serviceReady(processObj.serviceDetails):
            valid = False

        # Check if parameters make sense

        # Check if object(s) is/are printable

        # Check if dimensions fit

        # Check ....

        # But first, check if the status has been changed in the meantime (gone back or cancelled or something)
        sleep(3)
        currentProcessObj = DBProcessesAccess.ProcessManagementBase.getProcessObj("", processObj.processID)
        if currentProcessObj == None:
            # Process doesn't exist anymore
            return
        elif currentProcessObj.processStatus != processStatusAsInt(ProcessStatusAsString.VERIFYING):
            return # Not needed anymore
        
        # Get all details and set status in database    
        userOfThatProcess, orgaOrNot = ProfileManagementBase.getUserViaHash(processObj.client)
        locale = ProfileManagementBase.getUserLocale(hashedID=processObj.client)
        userEMailAddress = ProfileManagementBase.getEMailAddress(processObj.client)
        processTitle = processObj.processDetails[ProcessDetails.title] if ProcessDetails.title in processObj.processDetails else processObj.processID
        subject = Locales.manageTranslations.getTranslation(locale, ["email","subjects","statusUpdate"])
        if valid:
            message = Locales.manageTranslations.getTranslation(locale, ["email","content","verificationSuccessful"])
            DBProcessesAccess.ProcessManagementBase.updateProcess("", processObj.processID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.VERIFICATION_COMPLETED), "SYSTEM")
        else: # Else: set to failed
            message = Locales.manageTranslations.getTranslation(locale, ["email","content","verificationFailed"])
            DBProcessesAccess.ProcessManagementBase.updateProcess("", processObj.processID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.SERVICE_COMPLICATION), "SYSTEM")
        
        # send out mail & Websocket event 
        notificationPreferences = profileManagement[ProfileClasses.organization if orgaOrNot else ProfileClasses.user].getNotificationPreferences(processObj.client)
        showEvent = False
        if notificationPreferences is not None:
            if NotificationSettingsUserSemperKI.verification in notificationPreferences:
                if userEMailAddress is not None and notificationPreferences[NotificationSettingsUserSemperKI.verification][UserNotificationTargets.email] == True:
                    sendEMail(userEMailAddress, f"{subject} '{processTitle}'", userOfThatProcess.name, locale, message)
                if notificationPreferences[NotificationSettingsUserSemperKI.verification][UserNotificationTargets.event] == True:
                    showEvent = True
        websocket.fireWebsocketEventForClient(processObj.project.projectID, [processObj.processID], ProcessUpdates.processStatus, "", showEvent)  
        
    except Exception as error:
        loggerError.error(f"Error while verifying process: {str(error)}")

####################################################################
@runInBackground
def sendProcessEMails(processObj:Process, contractorObj:Organization, session):
    """
    Send the e-mails regarding the process on their merry way to the user and the contractor
    
    :param processObj: The process belonging to the project
    :type processObj: Process
    :param contractorObj: The contractor that the process is send to
    :type contractorObj: Organization
    :param session: The session of the user
    :type session: Django Session Object (dict-like)
    :return: Nothing
    :rtype: None

    """
    try:
        # Send email to contractor (async)
        notificationPreferencesContractor = ProfileManagementOrganization.getNotificationPreferences(contractorObj.hashedID)
        if notificationPreferencesContractor is not None and NotificationSettingsOrgaSemperKI.processReceived in notificationPreferencesContractor and notificationPreferencesContractor[NotificationSettingsOrgaSemperKI.processReceived][UserNotificationTargets.email] == True:
            locale = ProfileManagementBase.getUserLocale(hashedID=contractorObj.hashedID)
            contractorEMailAddress = ProfileManagementOrganization.getEMailAddress(contractorObj.hashedID)
            if contractorEMailAddress is not None:
                processTitle = processObj.processDetails[ProcessDetails.title] if ProcessDetails.title in processObj.processDetails else processObj.processID
                subject = Locales.manageTranslations.getTranslation(locale, ["email","subjects","newProcessForContractor"])
                message = Locales.manageTranslations.getTranslation(locale, ["email","content","newProcessForContractor"])
                sendEMail(contractorEMailAddress, subject, contractorObj.name, locale, f"{message} {processTitle}")

        # Send Mail to user that the process is on its way
        userObj, orgaOrNot = ProfileManagementBase.getUserViaHash(processObj.client)
        notificationPreferencesClient = profileManagement[ProfileClasses.organization if orgaOrNot else ProfileClasses.user].getNotificationPreferences(processObj.client)
        if notificationPreferencesClient is not None and NotificationSettingsUserSemperKI.processSent in notificationPreferencesClient and notificationPreferencesClient[NotificationSettingsUserSemperKI.processSent][UserNotificationTargets.email] == True:
            locale = ProfileManagementBase.getUserLocale(hashedID=processObj.client)
            userMailAddress = ProfileManagementBase.getEMailAddress(processObj.client)
            if userMailAddress is not None:
                subject = Locales.manageTranslations.getTranslation(locale, ["email","subjects","processSent"])
                message = Locales.manageTranslations.getTranslation(locale, ["email","content","processSent"])
                sendEMail(userMailAddress, f"{subject} '{processTitle}'", userObj.name, locale, message)

    except Exception as error:
        loggerError.error(f"Error while sending process: {str(error)}")


######################################################################
@runInBackground
def sendLocalFileToRemote(pathOnStorage:str):
    """
    Send a file from local storage to remote storage in the background

    :param pathOnStorage: The path on both s3 directories
    :type pathOnStorage: str
    :return: Nothing
    :rtype: None
    
    """
    try:
        FileHandler.moveFileToRemote(pathOnStorage, pathOnStorage)
    except Exception as error:
        loggerError.error(f"Error while sending file from local to remote: {str(error)}")