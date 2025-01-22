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
def sendEMail(IDOfReceiver:str, notification:str, subject:list[str], message:list[str], processTitle:str) -> None:
    """
    Send an E-Mail asynchronously

    :param IDOfReceiver: ID of receiving user/orga
    :type IDOfReceiver: str 
    :param notification: The notification setting
    :type notification: str
    :param subject: What the mail is about
    :type subject: str 
    :param message: The actual message
    :type message: str 
    :param processTitle: What is the process called?
    :type processTitle: str
    :return: Nothing
    :rtype: None
    
    """
    try:
        dictOfPreferences = DBProcessesAccess.gatherUserHashIDsAndNotificationPreference(IDOfReceiver, notification, UserNotificationTargets.email)
        for hashedID in dictOfPreferences:
            if dictOfPreferences[hashedID]: # person wants to receive an email about this
                userEMailAddress = ProfileManagementBase.getEMailAddress(hashedID)
                if userEMailAddress == None:
                    continue
                userLocale = ProfileManagementBase.getUserLocale(hashedID=hashedID)
                userName = ProfileManagementBase.getUserNameViaHash(hashedID)
                subjectOfMessage = Locales.manageTranslations.getTranslation(userLocale, subject)
                messageItself = Locales.manageTranslations.getTranslation(userLocale, message)
                mailer = MailingClass()
                mailer.sendMail(userEMailAddress, f"{subjectOfMessage} '{processTitle}'", mailer.mailingTemplate(userName, userLocale, messageItself) )
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
        if valid and not serviceManager.getService(processObj.serviceType).serviceReady(processObj.serviceDetails)[0]:
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
        processTitle = processObj.processDetails[ProcessDetails.title] if ProcessDetails.title in processObj.processDetails else processObj.processID
        subject = ["email","subjects","statusUpdate"]
        contentForEvent = ""
        if valid:
            message = ["email","content","verificationSuccessful"]
            retVal = DBProcessesAccess.ProcessManagementBase.updateProcess("", processObj.processID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.VERIFICATION_COMPLETED), "SYSTEM")
            if isinstance(retVal, Exception):
                raise retVal
            contentForEvent = retVal
        else: # Else: set to failed
            message = ["email","content","verificationFailed"]
            retVal = DBProcessesAccess.ProcessManagementBase.updateProcess("", processObj.processID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.SERVICE_COMPLICATION), "SYSTEM")
            if isinstance(retVal, Exception):
                raise retVal
            contentForEvent = retVal
        # send out mail & Websocket event 
        sendEMail(processObj.client, NotificationSettingsUserSemperKI.verification, subject, message, processTitle)
        websocket.fireWebsocketEventsForProcess(processObj.project.projectID, processObj.processID, session, ProcessUpdates.processStatus, contentForEvent, NotificationSettingsUserSemperKI.verification, True)  
        
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
        processTitle = processObj.processDetails[ProcessDetails.title] if ProcessDetails.title in processObj.processDetails else processObj.processID
        
        subject = ["email","subjects","newProcessForContractor"]
        message = ["email","content","newProcessForContractor"]
        sendEMail(contractorObj.hashedID, NotificationSettingsOrgaSemperKI.processReceived, subject, message, processTitle)

        # Send Mail to user that the process is on its way
        subject = ["email","subjects","processSent"]
        message = ["email","content","processSent"]
        sendEMail(processObj.client, NotificationSettingsUserSemperKI.processSent, subject, message, processTitle)

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