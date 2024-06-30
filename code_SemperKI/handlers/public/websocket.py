"""
Part of Semper-KI software

Akshay NS 2024

Contains: handlers for websockets
"""
import json, logging, copy
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities import crypto, rights
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient
from Generic_Backend.code_General.connections.postgresql import pgProfiles


from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.handlers.public.process import updateProcess

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

def fireWebsocketEvents(projectID, processIDArray, session, event, operation=""):
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
    :return: Nothing
    :rtype: None
    """
    if manualCheckifLoggedIn(session):
        dictForEvents = pgProcesses.ProcessManagementBase.getInfoAboutProjectForWebsocket(projectID, processIDArray, event)
        channel_layer = get_channel_layer()
        for userID in dictForEvents: # user/orga that is associated with that process
            values = dictForEvents[userID] # message, formatted for frontend
            subID = pgProfiles.ProfileManagementBase.getUserKeyViaHash(userID) # primary key
            if subID != pgProfiles.ProfileManagementBase.getUserKey(session=session) and subID != pgProfiles.ProfileManagementBase.getUserOrgaKey(session=session): # don't show a message for the user that changed it
                userKeyWOSC = pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=subID)
                for permission in rights.rightsManagement.getPermissionsNeededForPath(updateProcess.__name__):
                    if operation=="" or operation in permission:
                        async_to_sync(channel_layer.group_send)(userKeyWOSC+permission, {
                            "type": "sendMessageJSON",
                            "dict": values,
                        })
    else: # not logged in therefore no websockets to fire
        return
    

#######################################################
def fireWebsocketEventForClient(projectID, processIDArray, event, operation=""):
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
    :return: Nothing
    :rtype: None
    """

    dictForEvents = pgProcesses.ProcessManagementBase.getInfoAboutProjectForWebsocket(projectID, processIDArray, event)
    channel_layer = get_channel_layer()
    for userID in dictForEvents: # user/orga that is associated with that process
        values = dictForEvents[userID] # message, formatted for frontend
        subID = pgProfiles.ProfileManagementBase.getUserKeyViaHash(userID) # primary key
        userKeyWOSC = pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=subID)
        for permission in rights.rightsManagement.getPermissionsNeededForPath(updateProcess.__name__):
            if operation=="" or operation in permission:
                async_to_sync(channel_layer.group_send)(userKeyWOSC+permission, {
                    "type": "sendMessageJSON",
                    "dict": values,
                })
                
###########################################                