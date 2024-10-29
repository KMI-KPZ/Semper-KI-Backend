"""
Part of Semper-KI software

Akshay NS 2024

Contains: handlers for websockets
"""
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from Generic_Backend.code_General.definitions import *
#from Generic_Backend.code_General.utilities import rights
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn
#from Generic_Backend.code_General.connections.postgresql import pgProfiles


from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.definitions import *
#import code_SemperKI.handlers.public.process as ProcessFunctions
from code_SemperKI.utilities.basics import *
from code_SemperKI.connections.content.postgresql import pgEvents


logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
def fireWebsocketEventsForProcess(projectID:str, processID:str, session, event, eventContent, notification:str="", clientOnly:bool=False):
    """
    Fire websocket event from a list for a specific project and process. 
    
    :param projectID: The project ID
    :type projectID: Str
    :param processIDArray: The process IDs
    :type processIDArray: Str
    :param session: The session of the current user
    :type session: Dict
    :param event: The event to fire
    :type event: Str
    :param eventContent: The content that triggered this event, for event queue
    :type eventContent: Any
    :param notification: The type of notification
    :type notification: str
    :param clientOnly: Should the event fire only for the client, not the contractor
    :type clientOnly: Bool
    :return: Nothing
    :rtype: None
    """
    # TODO Fix calls to this function, set channels correctly with only userSubID, emails
    if manualCheckifLoggedIn(session):
        dictForEvents = pgProcesses.ProcessManagementBase.getInfoAboutProjectForWebsocket(projectID, processID, event, eventContent, notification, clientOnly)
        channelLayer = get_channel_layer()
        for userID, values in dictForEvents.items(): # user/orga that is associated with that process
            if notification == NotificationSettingsUserSemperKI.newMessage and userID == ProfileManagementBase.getUserHashID(session=session):
                continue # If you wrote a message, you shouldn't get a notification for yourself
            pgEvents.createEventEntry(userID, values) # create an entry in the event queue for that user
            async_to_sync(channelLayer.group_send)(userID[:80], {
                "type": "sendMessageJSON",
                "dict": values, # message, formatted for frontend
            })
    # not logged in therefore no websockets to fire
                        