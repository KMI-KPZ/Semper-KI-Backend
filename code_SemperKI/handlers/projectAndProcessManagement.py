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
from Generic_Backend.code_General.definitions import SessionContent, FileObjectContent, OrganizationDescription, UserDescription, GlobalDefaults, Logging, UserDetails
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, manualCheckifLoggedIn, manualCheckifAdmin, manualCheckIfRightsAreSufficient, manualCheckIfRightsAreSufficientForSpecificOperation
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from ..connections.content.postgresql import pgProcesses
from ..definitions import *
from ..serviceManager import serviceManager
from ..utilities.basics import manualCheckIfUserMaySeeProcess, checkIfUserMaySeeProcess, manualCheckIfUserMaySeeProject
from ..states.states import processStatusAsInt, ProcessStatusAsString, StateMachine, getButtonsForProcess, InterfaceForStateChange, signalDependencyToOtherProcesses, getFlatStatus
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

        # set default addresses here
        if manualCheckifLoggedIn(request.session):
            clientAddresses = pgProfiles.ProfileManagementBase.getUser(request.session)[UserDescription.details][UserDetails.addresses]
            defaultAddress = {}
            for key in clientAddresses:
                entry = clientAddresses[key]
                if entry["standard"]:
                    defaultAddress = entry
                    break
            addressesForProcess = {ProcessDetails.clientDeliverAddress: defaultAddress, ProcessDetails.clientBillingAddress: defaultAddress}
            interface.updateProcess(projectID, processID, ProcessUpdates.processDetails, addressesForProcess, client)

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

        # return just the generated ID for frontend
        return JsonResponse({ProcessDescription.processID: processID})
    except (Exception) as error:
        loggerError.error(f"createProcessID: {str(error)}")
        return JsonResponse({}, status=500)
    
#######################################################
def cloneProcess(request, oldProjectID:str, oldProcessIDs:list[str]):
    """
    Duplicate selected processes. Works only for logged in users.

    :param request: POST request from statusButtonRequest
    :type request: HTTP POST
    :param projectID: The project ID of the project the processes belonged to
    :type projectID: str
    :param processIDs: List of processes to be cloned
    :type processIDs: list of strings
    :return: JSON with project and process IDs
    :rtype: JSONResponse
    
    """
    try:
        outDict = {"projectID": "", "processIDs": []}

        # create new project with old information
        oldProject = pgProcesses.ProcessManagementBase.getProjectObj(oldProjectID)
        newProjectID = crypto.generateURLFriendlyRandomString()
        outDict["projectID"] = newProjectID
        errorOrNone = pgProcesses.ProcessManagementBase.createProject(newProjectID, oldProject.client)
        if isinstance(errorOrNone, Exception):
            raise errorOrNone
        pgProcesses.ProcessManagementBase.updateProject(newProjectID, ProjectUpdates.projectDetails, oldProject.projectDetails)
        if isinstance(errorOrNone, Exception):
            raise errorOrNone
        
        mapOfOldProcessIDsToNewOnes = {}
        # for every old process, create new process with old information
        for processID in oldProcessIDs:
            oldProcess = pgProcesses.ProcessManagementBase.getProcessObj(oldProjectID, processID) 
            newProcessID = crypto.generateURLFriendlyRandomString()
            outDict["processIDs"].append(newProcessID)
            mapOfOldProcessIDsToNewOnes[processID] = newProcessID
            errorOrNone = pgProcesses.ProcessManagementBase.createProcess(newProjectID, newProcessID, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            
            oldProcessDetails = copy.deepcopy(oldProcess.processDetails)
            del oldProcessDetails[ProcessDetails.provisionalContractor]
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.processDetails, oldProcessDetails, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            
            # copy files but with new fileID
            newFileDict = {}
            for fileKey in oldProcess.files:
                oldFile = oldProcess.files[fileKey]
                newFile = copy.deepcopy(oldFile)
                #newFileID = crypto.generateURLFriendlyRandomString()
                newFile[FileObjectContent.id] = fileKey
                newFilePath = newProcessID+"/"+fileKey
                newFile[FileObjectContent.path] = newFilePath
                newFile[FileObjectContent.date] = str(timezone.now())
                if oldFile[FileObjectContent.remote]:
                    s3.manageRemoteS3.copyFile("kiss/"+oldFile[FileObjectContent.path], newFilePath)
                else:
                    s3.manageLocalS3.copyFile(oldFile[FileObjectContent.path], newFilePath)
                newFileDict[fileKey] = newFile
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.files, newFileDict, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            
            # set service specific stuff
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.serviceType, oldProcess.serviceType, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            # set service details -> implementation in service (cloneServiceDetails)
            newProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, newProcessID) 
            errorOrNewDetails = serviceManager.getService(oldProcess.serviceType).cloneServiceDetails(oldProcess.serviceDetails, newProcess)
            if isinstance(errorOrNewDetails, Exception):
                raise errorOrNewDetails
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.serviceDetails, errorOrNewDetails, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone

        # all new processes must already be created here in order to link them accordingly
        for oldProcessID in mapOfOldProcessIDsToNewOnes:
            newProcessID = mapOfOldProcessIDsToNewOnes[oldProcessID]
            oldProcess = pgProcesses.ProcessManagementBase.getProcessObj(oldProjectID, oldProcessID)
            newProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, newProcessID)
            # connect the processes if they where dependend before
            for connectedOldProcessIn in oldProcess.dependenciesIn.all():
                if connectedOldProcessIn.processID in oldProcessIDs:
                    newConnectedProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, mapOfOldProcessIDsToNewOnes[connectedOldProcessIn.processID])
                    newProcess.dependenciesIn.add(newConnectedProcess)
            for connectedOldProcessIn in oldProcess.dependenciesOut.all():
                if connectedOldProcessIn.processID in oldProcessIDs:
                    newConnectedProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, mapOfOldProcessIDsToNewOnes[connectedOldProcessIn.processID])
                    newProcess.dependenciesOut.add(newConnectedProcess)
            newProcess.save()

            # set process state through state machine (could be complete or waiting or in conflict and so on)
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.SERVICE_IN_PROGRESS), oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            newProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, newProcessID)
            currentState = StateMachine(initialAsInt=newProcess.processStatus)
            contentManager = ManageContent(request.session)
            interface = contentManager.getCorrectInterface(cloneProcess.__name__)
            currentState.onUpdateEvent(interface, newProcess)

        return JsonResponse(outDict)
        
    except Exception as error:
        loggerError.error(f"Error when cloning processes: {error}")
        return JsonResponse({})

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
            
            # change state for this process if necessary
            process = interface.getProcessObj(projectID, processID)
            currentState = StateMachine(initialAsInt=process.processStatus)
            currentState.onUpdateEvent(interface, process)
            signalDependencyToOtherProcesses(interface, process)

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
        
        # TODO remove
        if ProcessUpdates.processStatus in changes["changes"]:
            del changes["changes"][ProcessUpdates.processStatus] # frontend shall not change status any more

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
def deleteProcessFunction(session, processIDs:list[str]):
    """
    Delete the processes

    :param session: The session
    :type session: Django session object (dict-like)
    :param processIDs: Array of proccess IDs 
    :type processIDs: list[str]
    :return: The response
    :rtype: HttpResponse | Exception

    """
    try:
        contentManager = ManageContent(session)
        interface = contentManager.getCorrectInterface(deleteProcesses.__name__)
        if interface == None:
            logger.error("Rights not sufficient in deleteProcesses")
            return HttpResponse("Insufficient rights!", status=401)

        for processID in processIDs:
            if not contentManager.checkRightsForProcess(processID):
                logger.error("Rights not sufficient in deleteProcesses")
                return HttpResponse("Insufficient rights!", status=401)
            interface.deleteProcess(processID)
            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))
        return HttpResponse("Success")
    
    except Exception as e:
        return e

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
        retVal = deleteProcessFunction(request.session, processIDs)
        if isinstance(retVal, Exception):
            raise retVal
        return retVal
        
    except (Exception) as error:
        loggerError.error(f"deleteProcess: {str(error)}")
        return HttpResponse("Failed",status=500)

################################################################################################
# retrieval

#######################################################
@require_http_methods(["GET"]) 
def getFlatProjects(request):
    """
    Retrieve all projects.

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with dict
    :rtype: JSON Response

    """
    try:
        outDict = {"projects": []}
        contentManager = ManageContent(request.session)

        # Gather from session...
        if contentManager.sessionManagement.getIfContentIsInSession():
            sessionContent = contentManager.sessionManagement.getProjectsFlat(request.session)
            outDict["projects"].extend(sessionContent)
        
        # ... and from database
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, getProcess.__name__):           
            objFromDB = contentManager.postgresManagement.getProjectsFlat(request.session)
            if len(objFromDB) >= 1:
                outDict["projects"].extend(objFromDB)

        outDict["projects"] = sorted(outDict["projects"], key=lambda x: 
                   timezone.make_aware(datetime.strptime(x[ProjectDescription.createdWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
        
        return JsonResponse(outDict)
    
    except (Exception) as error:
        loggerError.error(f"getFlatProjects: {str(error)}")
        
    return JsonResponse({})

#######################################################
@require_http_methods(["GET"]) 
def getProject(request, projectID):
    """
    Retrieve project with flat processes.

    :param request: GET Request
    :type request: HTTP GET
    :param projectID: id of the project
    :type projectID: str
    :return: Response with dict
    :rtype: JSON Response

    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(getProject.__name__)
        if interface == None:
            logger.error("Rights not sufficient in getProject")
            return JsonResponse({}, status=401)
        
        projectAsDict = interface.getProject(projectID)
        processList = projectAsDict[SessionContentSemperKI.processes]
        listOfFlatProcesses = []
        for entry in processList:
            flatProcessDict = {
                ProcessDetails.title: entry[ProcessDescription.processDetails][ProcessDetails.title] if ProcessDetails.title in entry[ProcessDescription.processDetails] else entry[ProcessDescription.processID],
                ProcessDescription.processID: entry[ProcessDescription.processID],
                ProcessDescription.serviceType: entry[ProcessDescription.serviceType],
                ProcessDescription.updatedWhen: entry[ProcessDescription.updatedWhen],
                ProcessDescription.createdWhen: entry[ProcessDescription.createdWhen],
                "flatProcessStatus": getFlatStatus(entry[ProcessDescription.processStatus], contentManager.getClient() == entry[ProcessDescription.client]),
                ProcessDetails.amount: entry[ProcessDescription.processDetails][ProcessDetails.amount] if ProcessDetails.amount in entry[ProcessDescription.processDetails] else 1,
                ProcessDetails.imagePath: entry[ProcessDescription.processDetails][ProcessDetails.imagePath] if ProcessDetails.imagePath in entry[ProcessDescription.processDetails] else ""
            }
            listOfFlatProcesses.append(flatProcessDict)

        projectAsDict[SessionContentSemperKI.processes] = listOfFlatProcesses
        return JsonResponse(projectAsDict)
    
    except (Exception) as error:
        loggerError.error(f"getProject: {str(error)}")
        
    return JsonResponse({})
    

#######################################################
@require_http_methods(["GET"]) 
def getProcess(request, projectID, processID):
    """
    Retrieve complete process.

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with list
    :rtype: JSON Response

    """
    try:
        contentManager = ManageContent(request.session)
        userID = contentManager.getClient()
        adminOrNot = manualCheckifAdmin(request.session)
        interface = contentManager.getCorrectInterface(getProject.__name__)
        if interface == None:
            logger.error("Rights not sufficient in getProject")
            return JsonResponse({}, status=401)

        process = interface.getProcessObj(projectID, processID)
        if isinstance(process, Exception):
            raise process

        buttons = getButtonsForProcess(process, process.client == userID, adminOrNot) # calls current node of the state machine
        outDict = process.toDict()
        outDict["processStatusButtons"] = buttons
        return JsonResponse(outDict)

    except (Exception) as error:
        loggerError.error(f"getProcess: {str(error)}")
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
def getContractors(request, processID:str):
    """
    Get all suitable Contractors.

    :param request: GET request
    :type request: HTTP GET
    :param processID: The ID of the process a contractor is chosen for
    :type processID: str
    :return: List of contractors and some details
    :rtype: JSON

    """
    # TODO filter 
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface() # checks not needed for rights, was done in the decorators
        processObj = interface.getProcessObj("", processID) # Login was required here so projectID not necessary
        if processObj == None:
            raise Exception("Process ID not found in session or db")
        serviceType = processObj.serviceType
        service = serviceManager.getService(processObj.serviceType)

        listOfFilteredContractors = service.getFilteredContractors(processObj)
        # Format coming back from SPARQL is [{"ServiceProviderName": {"type": "literal", "value": "..."}, "ID": {"type": "literal", "value": "..."}}]
        # Therefore parse it
        listOfResultingContractors = []
        for contractor in listOfFilteredContractors:
            idOfContractor = contractor["ID"]["value"]
            contractorContentFromDB = pgProfiles.ProfileManagementOrganization.getOrganization(hashedID=idOfContractor)
            if isinstance(contractorContentFromDB, Exception):
                raise contractorContentFromDB
            contractorToBeAdded = {OrganizationDescription.hashedID: contractorContentFromDB[OrganizationDescription.hashedID],
                                   OrganizationDescription.name: contractorContentFromDB[OrganizationDescription.name],
                                   OrganizationDescription.details: contractorContentFromDB[OrganizationDescription.details]}
            listOfResultingContractors.append(contractorToBeAdded)
        
        if len(listOfFilteredContractors) == 0:
            listOfResultingContractors = pgProcesses.ProcessManagementBase.getAllContractors(serviceType)

        return JsonResponse(listOfResultingContractors, safe=False)
    except (Exception) as error:
        loggerError.error(f"getContractors: {str(error)}")
        return HttpResponse(error, status=500)

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
@require_http_methods(["POST"]) # TODO, GET is only for debugging
def statusButtonRequest(request):
    """
    Button was clicked, so the state must change (transition inside state machine)
    
    :param request: POST Request
    :type request: HTTP POST
    :return: Response with new buttons
    :rtype: JSONResponse
    """
    try:
        # get from info, create correct object, initialize statemachine, switch state accordingly
        info = json.loads(request.body.decode("utf-8"))
        projectID = info[InterfaceForStateChange.projectID]
        processIDs = info[InterfaceForStateChange.processIDs]
        buttonData = info[InterfaceForStateChange.buttonData]
        if "deleteProcess" in buttonData[InterfaceForStateChange.type]:
            retVal = deleteProcessFunction(request.session, processIDs)
            if isinstance(retVal, Exception):
                raise retVal
            return retVal
        elif "cloneProcess" in buttonData[InterfaceForStateChange.type]:
            retVal = cloneProcess(request, projectID, processIDs)
            if isinstance(retVal, Exception):
                raise retVal
            return retVal
        else:
            nextState = buttonData[InterfaceForStateChange.targetStatus]

            contentManager = ManageContent(request.session)
            interface = contentManager.getCorrectInterface(statusButtonRequest.__name__)
            for processID in processIDs:
                process = interface.getProcessObj(projectID, processID)
                sm = StateMachine(initialAsInt=process.processStatus)
                sm.onButtonEvent(nextState, interface, process)

        return JsonResponse({})
    except Exception as e:
        loggerError.error(f"statusButtonRequest: {str(e)}")
        return JsonResponse({}, status=500)

#######################################################
@require_http_methods(["GET"])
def getStateMachine(request):
    """
    Print out the whole state machine and all transitions

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with graph in JSON Format
    :rtype: JSONResponse
    
    """
    sm = StateMachine(initialAsInt=0)
    paths = sm.showPaths()
    return JsonResponse(paths)

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
        processObj = pgProcesses.ProcessManagementBase.getProcessObj("", processID)

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
    