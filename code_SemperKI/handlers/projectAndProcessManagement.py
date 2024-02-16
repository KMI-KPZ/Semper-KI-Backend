"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers managing the projects and processes
"""

import json, logging, copy
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from Generic_Backend.code_General.utilities import crypto, rights
from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.definitions import SessionContent, FileObjectContent, OrganizationDescription, UserDescription, GlobalDefaults
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient, manualCheckIfRightsAreSufficientForSpecificOperation, Logging
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from ..connections.content.postgresql import pgProcesses
from ..definitions import *
from ..serviceManager import serviceManager
from ..utilities.basics import manualCheckIfUserMaySeeProcess, checkIfUserMaySeeProcess, manualCheckIfUserMaySeeProject
from ..connections.content.manageContent import ManageContent

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
################################################################################################

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

# Projects

#######################################################
@require_http_methods(["GET"])
def createProjectID(request):
    """
    Create project ID for frontend

    :param request: GET Request
    :type request: HTTP GET
    :return: project ID as string
    :rtype: JSONResponse

    """
    # generate ID string, make timestamp and create template for project
    projectID = crypto.generateURLFriendlyRandomString()
    #now = timezone.now()
    contentManager = ManageContent(request.session)
    interface = contentManager.getCorrectInterface(createProjectID.__name__)
    if interface == None:
        logger.error("Rights not sufficient in createProjectID")
        return JsonResponse({}, status=401)
    
    client = contentManager.getClient()
    interface.createProject(projectID, client)

    # login defines client
    #template = {ProjectDescription.projectID: projectID, ProcessDescription.client: "", ProjectDescription.projectStatus: 0, ProjectDescription.createdWhen: str(now), ProjectDescription.updatedWhen: str(now), ProjectDescription.projectDetails: {}, SessionContentSemperKI.processes: {}} 

    # if User is logged in, everything is database backend. For anonymous users, the cache suffices
    # if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, createProjectID.__name__):
    #     template[ProcessDescription.client] = pgProfiles.profileManagement[request.session[SessionContent.PG_PROFILE_CLASS]].getClientID(request.session)
    #     # save template only temporary in session and then in database
    #     request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID] = template
    #     pgProcesses.ProcessManagementBase.addProjectToDatabase(request.session)
    #     request.session[SessionContentSemperKI.CURRENT_PROJECTS].clear()
    #     del request.session[SessionContentSemperKI.CURRENT_PROJECTS]

    # else:
    #     # save project template in session for now
    #     request.session = sessionObj.createProject(projectID)

    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))

    #return just the id for the frontend
    return JsonResponse({ProjectDescription.projectID: projectID})

#######################################################
@require_http_methods(["PATCH"])
def updateProject(request):
    """
    Update stuff about the project

    :param request: Request with content
    :type request: HTTP PATCH
    :return: Message if it worked or not
    :rtype: HTTPResponse

    """
    try:
        changes = json.loads(request.body.decode("utf-8"))
        projectID = changes[ProjectDescription.projectID]

        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(updateProject.__name__)
        if interface == None or not contentManager.checkRightsForProject(projectID):
            logger.error("Rights not sufficient in updateProject")
            return HttpResponse("Insufficient rights!", status=401)

        for entry in changes["changes"]:
            returnVal = interface.updateProject(projectID, entry, changes["changes"][entry])
            if isinstance(returnVal, Exception):
                raise returnVal
              
        # TODO send to websockets that are active, that a new message/status is available for that project
        # outputDict = {EventsDescription.eventType: "projectEvent"}
        # outputDict["projectID"] = projectID
        # outputDict["projects"] = [{"projectID": projectID, "status": 1, "messages": 0}]
        # channel_layer = get_channel_layer()
        # listOfUsers = pgProcesses.ProcessManagementBase.getAllUsersOfProject(projectID)
        # for user in listOfUsers:
        #     if user.subID != pgProfiles.ProfileManagementBase.getUserKey(session=request.session):
        #         async_to_sync(channel_layer.group_send)(pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=user.subID), {
        #             "type": "sendMessageJSON",
        #             "dict": outputDict,
        #         })
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.EDITED},updated,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))

        return HttpResponse("Success")
    
    except (Exception) as error:
        loggerError.error(f"updateProject: {str(error)}")
        return HttpResponse("Failed",status=500)

#######################################################
@require_http_methods(["DELETE"])
def deleteProjects(request):
    """
    Delete the whole project

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param projectID: id of the project
    :type projectID: str
    :return: Success or not
    :rtype: HTTPRespone

    """
    try:
        projectIDs = request.GET['projectIDs'].split(",")
        #loggedIn = False # don't check rights in every iteration

        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(deleteProjects.__name__)
        if interface == None:
            logger.error("Rights not sufficient in deleteProjects")
            return HttpResponse("Insufficient rights!", status=401)
        
        for projectID in projectIDs:
            if not contentManager.checkRightsForProject(projectID):
                logger.error("Rights not sufficient in deleteProjects")
                return HttpResponse("Insufficient rights!", status=401)
            interface.deleteProject(projectID)
            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))
            """ if SessionContentSemperKI.CURRENT_PROJECTS in request.session and projectID in request.session[SessionContentSemperKI.CURRENT_PROJECTS]:
                for currentProjectID in request.session[SessionContentSemperKI.CURRENT_PROJECTS]:
                    if SessionContentSemperKI.processes in request.session[SessionContentSemperKI.CURRENT_PROJECTS][currentProjectID]:
                        for currentProcess in request.session[SessionContentSemperKI.CURRENT_PROJECTS][currentProjectID][SessionContentSemperKI.processes]:
                            for fileObj in request.session[SessionContentSemperKI.CURRENT_PROJECTS][currentProjectID][SessionContentSemperKI.processes][currentProcess][ProcessDescription.files]:
                                s3.manageLocalS3.deleteFile(request.session[SessionContentSemperKI.CURRENT_PROJECTS][currentProjectID][SessionContentSemperKI.processes][currentProcess][ProcessDescription.files][fileObj]["id"])
                del request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID]
                request.session.modified = True

            elif loggedIn or (manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, deleteProjects.__name__)):
                loggedIn = True
                userID = pgProfiles.profileManagement[request.session[SessionContent.PG_PROFILE_CLASS]].getClientID(request.session)
                if manualCheckIfUserMaySeeProject(request.session, userID, projectID) == False:
                    return HttpResponse("Not allowed!", status=401)
                
                pgProcesses.ProcessManagementBase.deleteProject(projectID)
            else:
                raise Exception("Not logged in or rights insufficient!") """
        
        return HttpResponse("Success")
    except (Exception) as error:
        loggerError.error(f"deleteProject: {str(error)}")
        return HttpResponse("Failed",status=500)
################################################################################################
# Processes

#######################################################
@require_http_methods(["GET"])
def createProcessID(request, projectID):
    """
    Create process ID for frontend

    :param request: GET Request
    :type request: HTTP GET
    :param projectID: id of the project the created process should belong to
    :type projectID: str
    :return: process ID as string
    :rtype: JSONResponse

    """
    try:
        # generate ID, timestamp and template for process
        processID = crypto.generateURLFriendlyRandomString()
        
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(createProcessID.__name__)
        if interface == None:
            logger.error("Rights not sufficient in createProcessID")
            return JsonResponse({}, status=401)
        
        client = contentManager.getClient()
        interface.createProcess(projectID, processID, client)

        """ 
        now = timezone.now()
        template = {ProcessDescription.processID: processID, 
                    ProcessDescription.client: "", 
                    ProcessDescription.processStatus: 0, 
                    ProcessDescription.processDetails: {ProcessDetails.amount: 1},
                    ProcessDescription.serviceStatus: 0, 
                    ProcessDescription.serviceType: serviceManager.getNone(), 
                    ProcessDescription.serviceDetails: {},
                    ProcessDescription.createdWhen: str(now), 
                    ProcessDescription.updatedWhen: str(now), 
                    ProcessDescription.files: {}, 
                    ProcessDescription.messages: {"messages": []} 
                    } # the last ones are just for in-session storage

        # save into respective project
        if SessionContentSemperKI.CURRENT_PROJECTS in request.session and projectID in request.session[SessionContentSemperKI.CURRENT_PROJECTS]:
            request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID] = template
            request.session.modified = True
            return JsonResponse({ProcessDescription.processID: processID})

        # else: it's in the database, fetch it from there
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, createProcessID.__name__):
            # get client ID
            client = pgProcesses.ProcessManagementBase.getProjectObj(projectID).client
            currentUserID = pgProfiles.profileManagement[request.session[SessionContent.PG_PROFILE_CLASS]].getClientID(request.session)
            if currentUserID != client:
                # No one except the client should be able to add a process to the project
                return JsonResponse({}, status=401)
            returnObj = pgProcesses.ProcessManagementBase.addProcessTemplateToProject(projectID, template, client)
            if isinstance(returnObj, Exception):
                raise returnObj
        """
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

        # return just the generated ID for frontend
        return JsonResponse({ProcessDescription.processID: processID})
    except (Exception) as error:
        loggerError.error(f"createProcessID: {str(error)}")
        return JsonResponse({}, status=500)

# #######################################################
# def updateProcessFunction(request, changes:dict, projectID:str, processIDs:list[str]):
#     """
#     Update process logic
    
#     :param projectID: Project ID
#     :type projectID: Str
#     :param projectID: Process ID
#     :type projectID: Str
#     :return: Message if it worked or not
#     :rtype: Str, bool or Error
#     """
#     try:
#         now = timezone.now()
#         if SessionContentSemperKI.CURRENT_PROJECTS in request.session and projectID in request.session[SessionContentSemperKI.CURRENT_PROJECTS]:
#             # changes
#             for processID in processIDs:
#                 # deletions
#                 if "deletions" in changes:
#                     for elem in changes["deletions"]:
#                         if elem == ProcessUpdates.messages:
#                             request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.messages]["messages"] = []
                    
#                         elif elem == ProcessUpdates.files:
#                             for entry in changes["deletions"][ProcessUpdates.files]:
#                                 del request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.files][entry]
                        
#                         elif elem == ProcessUpdates.serviceType:
#                             request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.serviceType] = serviceManager.getNone()
                        
#                         elif elem == ProcessUpdates.serviceDetails:
#                             serviceType = request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.serviceType]
#                             if serviceType != serviceManager.getNone():
#                                 request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.serviceDetails] = serviceManager.getService(serviceType).deleteServiceDetails(request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.serviceDetails], changes["deletions"][ProcessUpdates.serviceDetails])
#                             else:
#                                 raise Exception("No Service chosen!")
                        
#                         elif elem == ProcessUpdates.serviceStatus:
#                             request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.serviceStatus] = 0
                        
#                         elif elem == ProcessUpdates.processDetails:
#                             for entry in changes["deletions"][ProcessUpdates.processDetails]:
#                                 del request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.processDetails][entry]
                        
#                         elif elem == ProcessUpdates.processStatus:
#                             request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.processStatus] = ProcessStatus.DRAFT
                        
#                         elif elem == ProcessUpdates.provisionalContractor:
#                             del request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.processDetails][ProcessUpdates.provisionalContractor]

#                 for elem in changes["changes"]:
#                     if elem == ProcessUpdates.messages:
#                         request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.messages]["messages"].append(changes["changes"][ProcessUpdates.messages])
                    
#                     elif elem == ProcessUpdates.files:
#                         for entry in changes["changes"][ProcessUpdates.files]:
#                             request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.files][entry] = changes["changes"][ProcessUpdates.files][entry]
                    
#                     elif elem == ProcessUpdates.serviceType:
#                         request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.serviceType] = changes["changes"][ProcessUpdates.serviceType]
                    
#                     elif elem == ProcessUpdates.serviceDetails:
#                         serviceType = request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.serviceType]
#                         if serviceType != serviceManager.getNone():
#                             request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.serviceDetails] = serviceManager.getService(serviceType).updateServiceDetails(request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.serviceDetails], changes["changes"][ProcessUpdates.serviceDetails])
#                         else:
#                             raise Exception("No Service chosen!")
                    
#                     elif elem == ProcessUpdates.serviceStatus:
#                         request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.serviceStatus] = changes["changes"][ProcessUpdates.serviceStatus]
                    
#                     elif elem == ProcessUpdates.processDetails:
#                         for entry in changes["changes"][ProcessUpdates.processDetails]:
#                             request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.processDetails][entry] = changes["changes"][ProcessDescription.processDetails][entry]
                    
#                     elif elem == ProcessUpdates.processStatus:
#                         request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.processStatus] = changes["changes"][ProcessUpdates.processStatus]
                    
#                     elif elem == ProcessUpdates.provisionalContractor:
#                         request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.processDetails][ProcessUpdates.provisionalContractor] = changes["changes"][ProcessUpdates.provisionalContractor]

#                 request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID][ProcessDescription.updatedWhen] = str(now)
            
#             request.session.modified = True
#         else:
#             # database version
#             if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, updateProcess.__name__):
#                 userID = pgProfiles.profileManagement[request.session[SessionContent.PG_PROFILE_CLASS]].getClientID(request.session)

#                 for processID in processIDs:
#                     if manualCheckIfUserMaySeeProcess(request.session, userID, processID) == False:
#                         return ("", False) # user may not change this process
        
#                     if "deletions" in changes:
#                         for elem in changes["deletions"]:
#                             returnVal = True
#                             if elem == ProcessUpdates.serviceDetails: # service is a dict in itself      
#                                 returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, ProcessUpdates.serviceDetails, changes["deletions"][ProcessUpdates.serviceDetails], userID)
#                             elif elem == ProcessUpdates.messages and manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, "messages"):
#                                 returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, ProcessUpdates.messages, changes["deletions"][ProcessUpdates.messages], userID)
#                             elif elem == ProcessUpdates.files and manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, "files"):
#                                 returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, ProcessUpdates.files, changes["deletions"][ProcessUpdates.files], userID)
#                             elif elem == ProcessUpdates.provisionalContractor:
#                                 returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, ProcessUpdates.provisionalContractor, changes["deletions"][ProcessUpdates.provisionalContractor], userID)
#                             elif elem == ProcessUpdates.processDetails:
#                                 returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, ProcessUpdates.processDetails, changes["deletions"][ProcessUpdates.processDetails], userID)
#                             elif elem == ProcessUpdates.processStatus:
#                                 returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, ProcessUpdates.processStatus, changes["deletions"][ProcessUpdates.processStatus], userID)
#                             elif elem == ProcessUpdates.serviceType:
#                                 returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, ProcessUpdates.serviceType, changes["deletions"][ProcessUpdates.serviceType], userID)
#                             elif elem == ProcessUpdates.serviceStatus:
#                                 returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, ProcessUpdates.serviceStatus, changes["deletions"][ProcessUpdates.serviceStatus], userID)
#                             elif elem == ProcessUpdates.serviceDetails:
#                                 returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, ProcessUpdates.serviceDetails, changes["deletions"][ProcessUpdates.serviceDetails], userID)
#                             else:
#                                 raise Exception("updateProcess delete " + elem + " not implemented")
#                             if isinstance(returnVal, Exception):
#                                 raise returnVal

#                     for elem in changes["changes"]:
#                         returnVal = True
#                         if elem == ProcessUpdates.serviceType:
#                             returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, ProcessUpdates.serviceType, changes["changes"][ProcessUpdates.serviceType], userID)
#                             fireWebsocketEvents(projectID, [processID], request.session, ProcessDescription.serviceType, "edit")
                        
#                         elif elem == ProcessUpdates.messages and manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, "messages"):
#                             returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, ProcessUpdates.messages, changes["changes"][ProcessUpdates.messages], userID)
#                             fireWebsocketEvents(projectID, [processID], request.session, "messages", "messages")
                        
#                         elif elem == ProcessUpdates.files and manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, "files"):
#                             returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, ProcessUpdates.files, changes["changes"][ProcessUpdates.files], userID)
#                             fireWebsocketEvents(projectID, [processID], request.session, "files", "files")
                        
#                         elif elem == ProcessUpdates.serviceDetails:
#                             returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, ProcessUpdates.serviceDetails, changes["changes"][ProcessUpdates.serviceDetails], userID)
                        
#                         elif elem == ProcessUpdates.processDetails:
#                             returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, ProcessUpdates.processDetails, changes["changes"][ProcessUpdates.processDetails], userID)
                        
#                         elif elem == ProcessUpdates.processStatus:
#                             returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, ProcessUpdates.processStatus, changes["changes"][ProcessUpdates.processStatus], userID)
#                             fireWebsocketEvents(projectID, [processID], request.session, ProcessDescription.processStatus, "edit")
                        
#                         elif elem == ProcessUpdates.serviceStatus:
#                             returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, ProcessUpdates.serviceStatus, changes["changes"][ProcessUpdates.serviceStatus], userID)
                        
#                         elif elem == ProcessUpdates.provisionalContractor:
#                             returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, ProcessUpdates.provisionalContractor, changes["changes"][ProcessUpdates.provisionalContractor], userID)
                        
#                         else:
#                             raise Exception("updateProcess change " + elem + " not implemented")

#                         if isinstance(returnVal, Exception):
#                             raise returnVal
                    
#                     # logging
#                     logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.EDITED},updated,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

#             else:
#                 return ("", False)
            
#         return ("", True)
#     except (Exception) as error:
#         return (error, True)

#######################################################
def updateProcessFunction(request, changes:dict, projectID:str, processIDs:list[str]):
    """
    Update process logic
    
    :param projectID: Project ID
    :type projectID: Str
    :param projectID: Process ID
    :type projectID: Str
    :return: Message if it worked or not
    :rtype: Str, bool or Error
    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(updateProcess.__name__)
        if interface == None:
            logger.error("Rights not sufficient in updateProcess")
            return ("", False)
        
        client = contentManager.getClient()
        
        for processID in processIDs:
            if not contentManager.checkRightsForProcess(processID):
                logger.error("Rights not sufficient in updateProcess")
                return ("", False)
            
            if "deletions" in changes:
                for elem in changes["deletions"]:
                    # exclude people not having sufficient rights for that specific operation
                    if client != GlobalDefaults.anonymous and (elem == ProcessUpdates.messages or elem == ProcessUpdates.files):
                        if not manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, str(elem)):
                            logger.error("Rights not sufficient in updateProcess")
                            return ("", False)
                        
                    returnVal = interface.deleteFromProcess(projectID, processID, elem, changes["deletions"][elem], client)

                    if isinstance(returnVal, Exception):
                        raise returnVal

            if "changes" in changes:
                for elem in changes["changes"]:
                    # for websocket events
                    if client != GlobalDefaults.anonymous and (elem == ProcessUpdates.messages or elem == ProcessUpdates.files or elem == ProcessUpdates.processStatus or elem == ProcessUpdates.serviceStatus):
                        # exclude people not having sufficient rights for that specific operation
                        if (elem == ProcessUpdates.messages or elem == ProcessUpdates.files) and not manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, str(elem)):
                            logger.error("Rights not sufficient in updateProcess")
                            return ("", False)
                        fireWebsocketEvents(projectID, [processID], request.session, elem, elem)
                    
                    returnVal = interface.updateProcess(projectID, processID, elem, changes["changes"][elem], client)

                    if isinstance(returnVal, Exception):
                        raise returnVal

            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.EDITED},updated,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

        return ("", True)
    except (Exception) as error:
        return (error, True)
        
#######################################################
def getProcessAndProjectFromSession(session, processID):
    """
    Retrieve a specific process from the current session instead of the database
    
    :param session: Session of the current user
    :type session: Dict
    :param projectID: Process ID
    :type projectID: Str
    :return: Process or None
    :rtype: Dict or None
    """
    try:
        contentManager = ManageContent(session)
        if contentManager.sessionManagement.getIfContentIsInSession():
            return contentManager.sessionManagement.structuredSessionObj.getProcessAndProjectPerID(processID)
        else:
            return (None, None)
        # if SessionContentSemperKI.CURRENT_PROJECTS in session:
        #     for currentProjectID in session[SessionContentSemperKI.CURRENT_PROJECTS]:
        #         for currentProcessID in session[SessionContentSemperKI.CURRENT_PROJECTS][currentProjectID][SessionContentSemperKI.processes]:
        #             if currentProcessID == processID:
        #                 return (currentProjectID, session[SessionContentSemperKI.CURRENT_PROJECTS][currentProjectID][SessionContentSemperKI.processes][currentProcessID])
        # return (None, None)
    except (Exception) as error:
        loggerError.error(f"getProcessAndProjectFromSession: {str(error)}")
        return (None, None)


#######################################################
@require_http_methods(["PATCH"])
def updateProcess(request):
    """
    Update stuff about the process

    :param request: Request with content
    :type request: HTTP PATCH
    :return: Message if it worked or not
    :rtype: HTTPResponse

    """
    try:
        changes = json.loads(request.body.decode("utf-8"))
        projectID = changes["projectID"]
        processIDs = changes["processIDs"] # list of processIDs
        
        message, flag = updateProcessFunction(request, changes, projectID, processIDs)
        if flag is False:
            return HttpResponse("Not logged in", status=401)
        if isinstance(message, Exception):
            raise Exception(message)

        return HttpResponse("Success")
    except (Exception) as error:
        loggerError.error(f"updateProcess: {str(error)}")
        return HttpResponse("Failed",status=500)

#######################################################
@require_http_methods(["DELETE"])
def deleteProcesses(request, projectID):
    """
    Delete one or more processes

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param projectID: id of the project
    :type projectID: str
    :return: Success or not
    :rtype: HTTPRespone

    """
    try:
        processIDs = request.GET['processIDs'].split(",")

        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(deleteProcesses.__name__)
        if interface == None:
            logger.error("Rights not sufficient in deleteProcesses")
            return HttpResponse("Insufficient rights!", status=401)

        for processID in processIDs:
            if not contentManager.checkRightsForProcess(processID):
                logger.error("Rights not sufficient in deleteProcesses")
                return HttpResponse("Insufficient rights!", status=401)
            interface.deleteProcess(processID)
            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))
        
        return HttpResponse("Success")
    except (Exception) as error:
        loggerError.error(f"deleteProcess: {str(error)}")
        return HttpResponse("Failed",status=500)

################################################################################################
# retrieval

#######################################################
@require_http_methods(["GET"]) 
def getFlatProjects(request):
    """
    Retrieve projects without much detail.

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with list
    :rtype: JSON Response

    """
    try:
        outDict = {"projects": []}
        contentManager = ManageContent(request.session)

        # Gather from session...
        if contentManager.sessionManagement.getIfContentIsInSession():
            sessionContent = contentManager.sessionManagement.getProjectsFlat(request.session)
            outDict["projects"].extend(sessionContent)
        
        # ... or from database
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, getFlatProjects.__name__):           
            objFromDB = contentManager.postgresManagement.getProjectsFlat(request.session)
            if len(objFromDB) >= 1:
                outDict["projects"].extend(objFromDB)

        outDict["projects"] = sorted(outDict["projects"], key=lambda x: 
                   timezone.make_aware(datetime.strptime(x[ProjectDescription.createdWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
        
        return JsonResponse(outDict)
    
    except (Exception) as error:
        loggerError.error(f"getFlatProjects: {str(error)}")
        
    return JsonResponse({"projects": []})

#######################################################
@require_http_methods(["GET"]) 
def getProject(request, projectID):
    """
    Retrieve project and processes.

    :param request: GET Request
    :type request: HTTP GET
    :param projectID: id of the project
    :type projectID: str
    :return: Response with dict
    :rtype: JSON Response

    """
    try:
        contentManager = ManageContent(request.session)
        # Is the project inside the session?
        project = {}
        if contentManager.sessionManagement.getIfContentIsInSession():
            project = contentManager.sessionManagement.getProject(projectID)
        if len(project) > 0:
            return JsonResponse(project)
        else:
            # if not, look into database and check if the user or the contractor wants the project 
            interface = contentManager.getCorrectInterface(getProject.__name__)
            if interface == None:
                logger.error("Rights not sufficient in getProject")
                return JsonResponse({}, status=401)
            
            userID = contentManager.getClient()
            if pgProcesses.ProcessManagementBase.checkIfUserIsClient(userID, projectID=projectID):
                return JsonResponse(pgProcesses.ProcessManagementBase.getProject(projectID))
            else:
                if pgProfiles.ProfileManagementBase.checkIfUserIsInOrganization(request.session):
                    return JsonResponse(pgProcesses.ProcessManagementBase.getProjectForContractor(projectID, userID))
                else:
                    return JsonResponse({}, status=401)

        # if SessionContentSemperKI.CURRENT_PROJECTS in request.session:
        #     if projectID in request.session[SessionContentSemperKI.CURRENT_PROJECTS]:
        #         outDict = copy.deepcopy(request.session[SessionContentSemperKI.CURRENT_PROJECTS][projectID]) # copy the content
        #         outDict[SessionContentSemperKI.processes] = [outDict[SessionContentSemperKI.processes][process] for process in outDict[SessionContentSemperKI.processes]]
        #         return JsonResponse(outDict)
        
        # if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, getProject.__name__):
        #     userID = pgProfiles.profileManagement[request.session[SessionContent.PG_PROFILE_CLASS]].getClientID(request.session)
        #     if pgProcesses.ProcessManagementBase.checkIfUserIsClient(userID, projectID=projectID):
        #         return JsonResponse(pgProcesses.ProcessManagementBase.getProject(projectID))
        #     else:
        #         if pgProfiles.ProfileManagementBase.checkIfUserIsInOrganization(request.session):
        #             return JsonResponse(pgProcesses.ProcessManagementBase.getProjectForContractor(projectID, userID))
        #         else:
        #             return JsonResponse({}, status=401)

        # return JsonResponse({})
    except (Exception) as error:
        loggerError.error(f"getProject: {str(error)}")
        return JsonResponse({}, status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def retrieveProjects(request):
    """
    Retrieve all saved projects with processes.

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response with projects/processes of that user
    :rtype: JSON Response

    """

    return JsonResponse(pgProcesses.ProcessManagementBase.getProjects(request.session), safe=False)
    

#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def getMissedEvents(request):
    """
    Show how many events (chat messages ...) were missed since last login.

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response with numbers for every process and project
    :rtype: JSON Response

    """

    user = pgProfiles.ProfileManagementBase.getUser(request.session)
    lastLogin = timezone.make_aware(datetime.strptime(user[UserDescription.lastSeen], '%Y-%m-%d %H:%M:%S.%f+00:00'))
    projects = pgProcesses.ProcessManagementBase.getProjects(request.session)

    output = {EventsDescription.eventType: EventsDescription.projectEvent, EventsDescription.events: []}
    #TODO: organization events like role changed or something
    for project in projects:
        currentProject = {}
        currentProject[ProjectDescription.projectID] = project[ProjectDescription.projectID]
        processArray = []
        for process in project[SessionContentSemperKI.processes]:
            currentProcess = {}
            currentProcess[ProcessDescription.processID] = process[ProcessDescription.processID]
            newMessagesCount = 0
            chat = process[ProcessDescription.messages]["messages"]
            for messages in chat:
                if MessageContent.date in messages and lastLogin < timezone.make_aware(datetime.strptime(messages[MessageContent.date], '%Y-%m-%dT%H:%M:%S.%fZ')) and messages[MessageContent.userID] != user[UserDescription.hashedID]:
                    newMessagesCount += 1
            if lastLogin < timezone.make_aware(datetime.strptime(process[ProcessDescription.updatedWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')):
                status = 1
            else:
                status = 0
            
            # if something changed, save it. If not, discard
            if status !=0 or newMessagesCount != 0: 
                currentProcess[ProcessDescription.processStatus] = status
                currentProcess[ProcessDescription.messages] = newMessagesCount

                processArray.append(currentProcess)
        if len(processArray):
            currentProject[SessionContentSemperKI.processes] = processArray
            output[EventsDescription.events].append(currentProject)
    
    # set accessed time to now
    pgProfiles.ProfileManagementBase.setLoginTime(user[UserDescription.hashedID])

    return JsonResponse(output, status=200, safe=False)

################################################################################################
# Save, verify, send

##############################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
@checkIfUserMaySeeProcess(json=True)
def getContractors(request, processID):
    """
    Get all suitable Contractors.

    :param request: GET request
    :type request: HTTP GET
    :return: List of contractors and some details
    :rtype: JSON

    """
    # TODO filter 
    try:
        projectObj, processObj = getProcessAndProjectFromSession(request.session,processID)
        if processObj == None:
            processObj = pgProcesses.ProcessManagementBase.getProcessObj(processID)
            if processObj == None:
                raise Exception("Process ID not found in session or db")
            else: # db
                serviceType = processObj.serviceType
        else: # session
            serviceType = processObj[ProcessDescription.serviceType]

        listOfAllContractors = pgProcesses.ProcessManagementBase.getAllContractors(serviceType)
        # TODO Check suitability

        # remove unnecessary information and add identifier
        # for idx, elem in enumerate(listOfAllContractors):
        #     contractorList.append({})
        #     contractorList[idx]["name"] = elem["name"]
        #     contractorList[idx]["id"] = elem["hashedID"]

        return JsonResponse(listOfAllContractors, safe=False)
    except (Exception) as error:
        loggerError.error(f"getContractors: {str(error)}")
        return error

#######################################################
def saveProjectsViaWebsocket(session):
    """
    Save projects to database

    :param session: session of user
    :type session: Dict
    :return: None
    :rtype: None

    """
    try:
        contentManager = ManageContent(session)
        if contentManager.sessionManagement.structuredSessionObj.getIfContentIsInSession() and contentManager.checkRights("saveProjects"):
            error = pgProcesses.ProcessManagementBase.addProjectToDatabase(session)
            if isinstance(error, Exception):
                raise error
            
            contentManager.sessionManagement.structuredSessionObj.clearContentFromSession()

            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(session)},{Logging.Predicate.PREDICATE},saved,{Logging.Object.OBJECT},their projects," + str(datetime.now()))
        return None
    
    except (Exception) as error:
        loggerError.error(f"saveProjectsViaWebsocket: {str(error)}")
        return error

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"]) 
@checkIfRightsAreSufficient(json=False)
def saveProjects(request):
    """
    Save projects to database

    :param request: GET Request
    :type request: HTTP GET
    :return: Response if sent successfully or not
    :rtype: HTTP Response

    """

    try:
        contentManager = ManageContent(request.session)
        if contentManager.sessionManagement.structuredSessionObj.getIfContentIsInSession():
            error = pgProcesses.ProcessManagementBase.addProjectToDatabase(request.session)
            if isinstance(error, Exception):
                raise error

            contentManager.sessionManagement.structuredSessionObj.clearContentFromSession()

            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.PREDICATE},saved,{Logging.Object.OBJECT},their projects," + str(datetime.now()))
        
        return HttpResponse("Success")
    
    except (Exception) as error:
        loggerError.error(f"saveProjects: {str(error)}")
        return HttpResponse("Failed")
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"]) 
@checkIfRightsAreSufficient(json=False)
def verifyProject(request):
    """
    Start calculations on server and set status accordingly

    :param request: PATCH Request
    :type request: HTTP PATCH
    :return: Response if processes are started successfully
    :rtype: HTTP Response

    """
    try:
        # get information
        info = json.loads(request.body.decode("utf-8"))
        projectID = info["projectID"]
        sendToContractorAfterVerification = info["send"]
        processesIDArray = info["processIDs"]
        userID = pgProfiles.profileManagement[request.session[SessionContent.PG_PROFILE_CLASS]].getClientID(request.session)

        if manualCheckIfUserMaySeeProject(request.session, userID, projectID) == False:
            return HttpResponse("Not allowed!", status=401)

        # first save projects
        contentManager = ManageContent(request.session)
        if contentManager.sessionManagement.structuredSessionObj.getIfContentIsInSession():
            error = pgProcesses.ProcessManagementBase.addProjectToDatabase(request.session)
            if isinstance(error, Exception):
                raise error

            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.PREDICATE},saved,{Logging.Object.OBJECT},their projects," + str(datetime.now()))
            
            # then clear drafts from session
            
            contentManager.sessionManagement.structuredSessionObj.clearContentFromSession()

        # TODO start services and set status to "verifying" instead of verified
        #listOfCallIDsAndProcessesIDs = []
        for entry in processesIDArray:
            pgProcesses.ProcessManagementBase.updateProcess(projectID, entry, ProcessUpdates.processStatus, ProcessStatus.VERIFIED, userID)
            #call = price.calculatePrice_Mock.delay([1,2,3]) # placeholder for each thing like model, material, post-processing
            #listOfCallIDsAndProcessesIDs.append((call.id, entry, collectAndSend.EnumResultType.price))

        # start collecting process, 
        #collectAndSend.waitForResultAndSendProcess(listOfCallIDsAndProcessesIDs, sendToManufacturerAfterVerification)

        # TODO Websocket Event

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.PREDICATE},verify,{Logging.Object.OBJECT},process {projectID}," + str(datetime.now()))

        if sendToContractorAfterVerification:
            sendProject(request)

        return HttpResponse("Success")
    
    except (Exception) as error:
        loggerError.error(f"verifyProject: {str(error)}")
        return HttpResponse("Failed")
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"]) 
@checkIfRightsAreSufficient(json=False)
def sendProject(request):
    """
    Retrieve Calculations and send process to contractor(s)

    :param request: PATCH Request
    :type request: HTTP PATCH
    :return: Response if processes are started successfully
    :rtype: HTTP Response

    """
    try:
        info = json.loads(request.body.decode("utf-8"))
        projectID = info["projectID"]
        processesIDArray = info["processIDs"]
        userID = pgProfiles.profileManagement[request.session[SessionContent.PG_PROFILE_CLASS]].getClientID(request.session)
        
        if manualCheckIfUserMaySeeProject(request.session, userID, projectID) == False:
            return HttpResponse("Not allowed!", status=401)
        
        # TODO Check if process is verified
        
        for entry in processesIDArray:
            pgProcesses.ProcessManagementBase.updateProcess(projectID, entry, ProcessUpdates.processStatus, ProcessStatus.REQUESTED, userID)
            pgProcesses.ProcessManagementBase.sendProcess(entry)

        # TODO send local files to remote

        # websocket event
        fireWebsocketEvents(projectID, processesIDArray, request.session, ProcessDescription.processStatus)

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.PREDICATE},sent,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))
        
        return HttpResponse("Success")
    
    except (Exception) as error:
        loggerError.error(f"sendProject: {str(error)}")
        return HttpResponse("Failed")


#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"]) 
@checkIfRightsAreSufficient(json=True)
@checkIfUserMaySeeProcess(json=True)
def getProcessHistory(request, processID):
    """
    See who has done what and when

    :param request: GET Request
    :type request: HTTP GET
    :param processID: The process of interest
    :type processID: str
    :return: JSON of process history
    :rtype: JSON Response

    """
    try:
        processObj = pgProcesses.ProcessManagementBase.getProcessObj(processID)

        if processObj == None:
            raise Exception("Process not found in DB!")
        
        listOfData = pgProcesses.ProcessManagementBase.getData(processID, processObj)
        # parse for frontend
        for index, entry in enumerate(listOfData):
            outDatum = {}
            outDatum[DataDescription.createdBy] = pgProfiles.ProfileManagementBase.getUserNameViaHash(entry[DataDescription.createdBy])
            outDatum[DataDescription.createdWhen] = entry[DataDescription.createdWhen]
            outDatum[DataDescription.type] = entry[DataDescription.type]
            outDatum[DataDescription.data] = entry[DataDescription.data]
            listOfData[index] = outDatum # overwrite

        outObj = {"history": listOfData}

        return JsonResponse(outObj)
    
    except (Exception) as error:
        loggerError.error(f"viewProcessHistory: {str(error)}")
        return JsonResponse({}, status=500)
    