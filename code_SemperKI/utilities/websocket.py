"""
Part of Semper-KI software

Akshay NS 2024

Contains: handlers for websockets
"""
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities import rights
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn
from Generic_Backend.code_General.connections.postgresql import pgProfiles


from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.definitions import *
import code_SemperKI.handlers.public.process as ProcessFunctions
from code_SemperKI.utilities.basics import *


logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
def fireWebsocketEvents(projectID, processID, session, event, notification:str, operation=""):
    """
    Fire websocket event from a list for a specific project and process. 
    If it should fire for only specific operations like messages or files, specify so.
    
    :param projectID: The project ID
    :type projectID: Str
    :param processIDArray: The process IDs
    :type processIDArray: Str
    :param session: The session of the current user
    :type session: Dict
    :param event: The event to fire
    :type event: Str
    :param notification: The type of notification
    :type notification: str
    :param operation: Nothing or messages, files, ...
    :type operation: Str
    :return: Nothing
    :rtype: None
    """
    # TODO Fix calls to this function, set channels correctly with only userSubID, emails
    if manualCheckifLoggedIn(session):
        dictForEvents = pgProcesses.ProcessManagementBase.getInfoAboutProjectForWebsocket(projectID, processID, event, notification)
        channel_layer = get_channel_layer()
        for userID in dictForEvents: # user/orga that is associated with that process
            values = dictForEvents[userID] # message, formatted for frontend
            userKeyWOSC = pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=userID)
            async_to_sync(channel_layer.group_send)(userKeyWOSC, {
                "type": "sendMessageJSON",
                "dict": values,
            })
    else: # not logged in therefore no websockets to fire
        return
    

#######################################################
def fireWebsocketEventForClient(projectID, processIDArray, event, operation="", notificationPreference=False):
    """
    Fire websocket event from a list for a specific project and process. 
    If it should fire for only specific operations like messages or files, specify so.
    
    :param projectID: The project ID
    :type projectID: Str
    :param processIDArray: The process IDs
    :type processIDArray: list(Str)
    :param session: The session of the current user
    :type session: Dict
    :param event: The event to fire
    :type event: Str
    :param operation: Nothing or messages, files, ...
    :type operation: Str
    :param notificationPreference: Send the frontend a hint if a toast should appear or not
    :type notificationPreference: bool
    :return: Nothing
    :rtype: None
    """
    
    dictForEvents = pgProcesses.ProcessManagementBase.getInfoAboutProjectForWebsocket(projectID, processIDArray, event)
    channel_layer = get_channel_layer()
    for userID in dictForEvents: # user/orga that is associated with that process
        values = dictForEvents[userID] # message, formatted for frontend
        values["triggerEvent"] = notificationPreference
        subID = pgProfiles.ProfileManagementBase.getUserKeyViaHash(userID) # primary key
        userKeyWOSC = pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=subID)
        for permission in rights.rightsManagement.getPermissionsNeededForPath(ProcessFunctions.updateProcess.cls.__name__):
            if operation=="" or operation in permission:
                async_to_sync(channel_layer.group_send)(userKeyWOSC+permission, {
                    "type": "sendMessageJSON",
                    "dict": values,
                })
                
###########################################                