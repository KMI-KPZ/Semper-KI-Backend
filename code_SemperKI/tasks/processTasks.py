"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Tasks that are needed for almost every process 
            and which shall be run in the background
"""
from django.conf import settings

from Generic_Backend.code_General.connections.mailer import MailingClass
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase
from Generic_Backend.code_General.definitions import SessionContent, UserDetails
from Generic_Backend.code_General.modelFiles.userModel import UserDescription

from ..utilities.asyncTask import runInBackground
from ..definitions import ProcessDescription, ProcessUpdates
from ..utilities.states.stateDescriptions import ProcessStatusAsString, processStatusAsInt
from ..modelFiles.processModel import Process
from ..serviceManager import serviceManager
import code_SemperKI.connections.content.postgresql.pgProcesses as DBProcessesAccess
import code_SemperKI.handlers.projectAndProcessManagement as ProjectAndProcessManagement

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

    valid = True
    # Check if service was correctly defined
    if valid and not serviceManager.getService(processObj.serviceType).serviceReady(processObj.serviceDetails):
        valid = False

    # Check if parameters make sense

    # Check if object(s) is/are printable

    # Check if dimensions fit

    # Check ....

    # If successful: set status in database & send out mail & Websocket event 
    userOfThatProcess = ProfileManagementBase.getUser(session)
    userEMailAdress = userOfThatProcess[UserDescription.details][UserDetails.email]
    mailer = MailingClass()
    if valid:
        DBProcessesAccess.ProcessManagementBase.updateProcess("", processObj.processID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.VERIFIED), "SYSTEM")
        ProjectAndProcessManagement.fireWebsocketEvents(processObj.project.projectID, [processObj.processID], session, ProcessUpdates.processStatus)
        mailer.sendMail(userEMailAdress, userEMailAdress, mailer.mailingTemplate(userOfThatProcess[UserDescription.name], "de-DE", "VERIFIKATION ERFOLGREICH") )
    # Else: send out mail & websocket event, that it failed
    else:
        DBProcessesAccess.ProcessManagementBase.updateProcess("", processObj.processID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.SERVICE_COMPLICATION), "SYSTEM")
        ProjectAndProcessManagement.fireWebsocketEvents(processObj.project.projectID, [processObj.processID], session, ProcessUpdates.processStatus)
        mailer.sendMail(userEMailAdress, userEMailAdress, mailer.mailingTemplate(userOfThatProcess[UserDescription.name], "de-DE", "VERIFIKATION GESCHEITERT") )