"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers managing the projects and processes
"""

import json, logging
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ..utilities import crypto, rights

from ..services.postgresDB import pgProcesses, pgProfiles

from ..utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient, manualCheckIfRightsAreSufficientForSpecificOperation, Logging, ProcessStatus

from ..services import aws

logger = logging.getLogger("logToFile")
################################################################################################

#######################################################

def fireWebsocketEvents(projectID, processID, session, event, operation=""):
    """
    Fire websocket event from a list for a specific project and process. 
    If it should fire for only specific operations like messages or files, specify so.
    
    :param projectID: The project ID
    :type projectID: Str
    :param processID: The process ID
    :type processID: Str
    :param session: The session of the current user
    :type session: Dict
    :param event: The event to fire
    :type event: Str
    :param operation: Nothing or messages, files, ...
    :type operation: Str
    :return: Nothing
    :rtype: None
    """
 
    dictForEvents = pgProcesses.ProcessManagementBase.getInfoAboutProjectForWebsocket(projectID, [processID], event)
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
    now = timezone.now()

    # login defines client
    if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, createProjectID.__name__):
        template = {"projectID": projectID, "client": pgProfiles.profileManagement[request.session["pgProfileClass"]].getClientID(request.session), "status": 0, "created": str(now), "updated": str(now), "details": {}, "processes": {}} 
    else:
        template = {"projectID": projectID, "client": "", "status": 0, "created": str(now), "updated": str(now), "details": {}, "processes": {}} 
    
    # save project template in session for now
    if "currentProjects" not in request.session:
        request.session["currentProjects"] = {}
    request.session["currentProjects"][projectID] = template
    request.session.modified = True

    #return just the id for the frontend
    return JsonResponse({"projectID": projectID})

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
        projectID = changes["projectID"]

        if "currentProjects" in request.session and projectID in request.session["currentProjects"]:
            if "status" in changes["changes"]:
                request.session["currentProjects"][projectID]["status"] = changes["changes"]["status"]
            elif "details" in changes["changes"]:
                for elem in changes["changes"]["details"]:
                    request.session["currentProjects"][projectID]["details"][elem] = changes["changes"]["details"][elem]
            request.session.modified = True
        else:
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, updateProject.__name__):
                if "status" in changes["changes"]:
                    returnVal = pgProcesses.ProcessManagementBase.updateProject(projectID, pgProcesses.EnumUpdates.status, changes["changes"]["status"])
                    if isinstance(returnVal, Exception):
                        raise returnVal
                if "details" in changes["changes"]:
                    returnVal = pgProcesses.ProcessManagementBase.updateProject(projectID, pgProcesses.EnumUpdates.details, changes["changes"]["details"])
                    if isinstance(returnVal, Exception):
                        raise returnVal
                
                # TODO send to websockets that are active, that a new message/status is available for that project
                # outputDict = {"eventType": "projectEvent"}
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

            else:
                return HttpResponse("Not logged in", status=401)

        return HttpResponse("Success")
    except (Exception) as error:
        logger.error(f"updateProject: {str(error)}")
        return HttpResponse("Failed",status=500)

#######################################################
@require_http_methods(["DELETE"])
def deleteProject(request, projectID):
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
        if "currentProjects" in request.session and projectID in request.session["currentProjects"]:
            for currentProjectID in request.session["currentProjects"]:
                for currentProcess in request.session["currentProjects"][currentProjectID]["processes"]:
                    for fileObj in request.session["currentProjects"][currentProjectID]["processes"][currentProcess]["files"]:
                        aws.manageLocalAWS.deleteFile(request.session["currentProjects"][currentProjectID]["processes"][currentProcess]["files"][fileObj]["id"])
            del request.session["currentProjects"][projectID]
            request.session.modified = True

        elif manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, deleteProject.__name__):
            pgProcesses.ProcessManagementBase.deleteProject(projectID)
        else:
            raise Exception("Not logged in or rights insufficient!")

        return HttpResponse("Success")
    except (Exception) as error:
        logger.error(f"deleteProject: {str(error)}")
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
        now = timezone.now()
        clientID = request.session["currentProjects"][projectID]["client"]
        template = {"processID": processID, "client": clientID, "contractor": [], "status": 0, "serviceStatus": 0, "created": str(now), "updated": str(now), "files": {}, "details": {}, "messages": {"messages": []}, "service": {"type": 0}}

        # save into respective project
        if "currentProjects" in request.session and projectID in request.session["currentProjects"]:
            request.session["currentProjects"][projectID]["processes"][processID] = template
            request.session.modified = True
            return JsonResponse({"processID": processID})

        # else: it's in the database, fetch it from there
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, createProcessID.__name__):
            # get client ID
            client = pgProcesses.ProcessManagementBase.getProjectObj(projectID).client
            returnObj = pgProcesses.ProcessManagementBase.addProcessTemplateToProject(projectID, template, client)
            if isinstance(returnObj, Exception):
                raise returnObj

        # return just the generated ID for frontend
        return JsonResponse({"processID": processID})
    except (Exception) as error:
        logger.error(f"createProcessID: {str(error)}")
        return JsonResponse({}, status=500)

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
        now = timezone.now()
        if "currentProjects" in request.session and projectID in request.session["currentProjects"]:
            # changes
            for processID in processIDs:
                for elem in changes["changes"]:
                    if elem == "service": # service is a dict in itself
                        if "type" in changes["changes"]["service"] and changes["changes"]["service"]["type"] == 0:
                                request.session["currentProjects"][projectID]["processes"][processID] = {"processID": processID, "contractor": [], "status": 0, "serviceStatus": 0, "created": str(now), "updated": str(now), "files": {"files" : []}, "details": {}, "messages": {"messages": []}, "service": {}}
                        else:
                            for entry in changes["changes"]["service"]:
                                request.session["currentProjects"][projectID]["processes"][processID]["service"][entry] = changes["changes"]["service"][entry]
                    elif elem == "messages":
                        request.session["currentProjects"][projectID]["processes"][processID]["messages"]["messages"].append(changes["changes"]["messages"])
                    elif elem == "files":
                        for entry in changes["changes"]["files"]:
                            request.session["currentProjects"][projectID]["processes"][processID]["files"][entry] = changes["changes"]["files"][entry]
                        # status, contractor
                    elif elem == "details":
                        for entry in changes["changes"]["details"]:
                            request.session["currentProjects"][projectID]["processes"][processID]["details"][entry] = changes["changes"]["details"][entry]
                    else:
                        request.session["currentProjects"][projectID]["processes"][processID][elem] = changes["changes"][elem]
                # deletions
                if "deletions" in changes:
                    for elem in changes["deletions"]:
                        if len(changes["deletions"][elem]) > 0:
                            for entry in changes["deletions"][elem]:
                                del request.session["currentProjects"][projectID]["processes"][processID][elem][entry]
                        else:
                            del request.session["currentProjects"][projectID]["processes"][processID][elem]
            
                request.session["currentProjects"][projectID]["processes"][processID]["updated"] = str(now)
            
            request.session.modified = True
        else:
            # database version
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, updateProcess.__name__):
                for processID in processIDs:
                    for elem in changes["changes"]:
                        returnVal = True
                        if elem == "service": # service is a dict in itself
                            if "type" in changes["changes"]["service"] and changes["changes"]["service"]["type"] == 0:
                                returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, pgProcesses.EnumUpdates.service, {})
                            else:        
                                returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, pgProcesses.EnumUpdates.service, changes["changes"]["service"])
                            fireWebsocketEvents(projectID, processID, request.session, "service", "edit")
                        elif elem == "messages" and manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, "messages"):
                            returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, pgProcesses.EnumUpdates.messages, changes["changes"]["messages"])
                            fireWebsocketEvents(projectID, processID, request.session, "messages", "messages")
                        elif elem == "files" and manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, "files"):
                            returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, pgProcesses.EnumUpdates.files, changes["changes"]["files"])
                            fireWebsocketEvents(projectID, processID, request.session, "files", "files")
                        elif elem == "contractor":
                            returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, pgProcesses.EnumUpdates.contractor, changes["changes"]["contractor"])
                        elif elem == "details":
                            returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, pgProcesses.EnumUpdates.details, changes["changes"]["details"])
                        elif elem == "status":
                            returnVal = pgProcesses.ProcessManagementBase.updateProcess(processID, pgProcesses.EnumUpdates.status, changes["changes"]["status"])
                            fireWebsocketEvents(projectID, processID, request.session, "status", "edit")
                        else:
                            raise Exception("updateProcess change " + elem + " not implemented")

                        if isinstance(returnVal, Exception):
                            raise returnVal
                    if "deletions" in changes:
                        for elem in changes["deletions"]:
                            returnVal = True
                            if elem == "service": # service is a dict in itself      
                                returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, pgProcesses.EnumUpdates.service, changes["deletions"]["service"])
                            elif elem == "messages" and manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, "messages"):
                                returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, pgProcesses.EnumUpdates.messages, changes["deletions"]["messages"])
                            elif elem == "files" and manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, "files"):
                                returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, pgProcesses.EnumUpdates.files, changes["deletions"]["files"])
                            elif elem == "contractor":
                                returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, pgProcesses.EnumUpdates.contractor, changes["deletions"]["contractor"])
                            elif elem == "details":
                                returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, pgProcesses.EnumUpdates.details, changes["deletions"]["details"])
                            elif elem == "status":
                                returnVal = pgProcesses.ProcessManagementBase.deleteFromProcess(processID, pgProcesses.EnumUpdates.status, changes["deletions"]["status"])
                            else:
                                raise Exception("updateProcess delete " + elem + " not implemented")
                            if isinstance(returnVal, Exception):
                                raise returnVal
                    # logging
                    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.EDITED},updated,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

            else:
                return ("", False)
            
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
        if "currentProjects" in session:
            for currentProjectID in session["currentProjects"]:
                for currentProcessID in session["currentProjects"][currentProjectID]["processes"]:
                    if currentProcessID == processID:
                        return (currentProjectID, session["currentProjects"][currentProjectID]["processes"][currentProcessID])
        return (None, None)
    except (Exception) as error:
        logger.error(f"getProcessAndProjectFromSession: {str(error)}")
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
            raise message

        return HttpResponse("Success")
    except (Exception) as error:
        logger.error(f"updateProcess: {str(error)}")
        return HttpResponse("Failed",status=500)

#######################################################
@require_http_methods(["DELETE"])
def deleteProcess(request, projectID):
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
        body = json.loads(request.body.decode("utf-8"))
        processIDs = body["processIDs"]
        for processID in processIDs:
            if "currentProjects" in request.session and projectID in request.session["currentProjects"]:
                for fileObj in request.session["currentProjects"][projectID]["processes"][processID]["files"]:
                    aws.manageLocalAWS.deleteFile(request.session["currentProjects"][projectID]["processes"][processID]["files"][fileObj]["id"])
                
                del request.session["currentProjects"][projectID]["processes"][processID]
                request.session.modified = True

            elif manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, deleteProcess.__name__):
                pgProcesses.ProcessManagementBase.deleteProcess(processID)
            else:
                raise Exception("Not logged in or rights insufficient!")
        
        return HttpResponse("Success")
    except (Exception) as error:
        logger.error(f"deleteProcess: {str(error)}")
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
        # From session
        if "currentProjects" in request.session:
            for entry in request.session["currentProjects"]:
                tempDict = {}
                tempDict["projectID"] = request.session["currentProjects"][entry]["projectID"]
                tempDict["client"] = request.session["currentProjects"][entry]["client"]
                tempDict["status"] =  request.session["currentProjects"][entry]["status"]
                tempDict["created"] = request.session["currentProjects"][entry]["created"]
                tempDict["updated"] = request.session["currentProjects"][entry]["updated"]
                tempDict["details"] = request.session["currentProjects"][entry]["details"]
                tempDict["processesCount"] = len(request.session["currentProjects"][entry]["processes"])
                outDict["projects"].append(tempDict)
        
        # From Database
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, getFlatProjects.__name__):
            objFromDB = pgProcesses.processManagement[request.session["pgProcessClass"]].getProjectsFlat(request.session)
            if len(objFromDB) >= 1:
                outDict["projects"].extend(objFromDB)

        return JsonResponse(outDict)
    
    except (Exception) as error:
        logger.error(f"getFlatProjects: {str(error)}")
        
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
        outDict = {}
        if "currentProjects" in request.session:
            if projectID in request.session["currentProjects"]:
                outDict["projectID"] = request.session["currentProjects"][projectID]["projectID"]
                outDict["client"] = request.session["currentProjects"][projectID]["client"]
                outDict["status"] =  request.session["currentProjects"][projectID]["status"]
                outDict["created"] = request.session["currentProjects"][projectID]["created"]
                outDict["updated"] = request.session["currentProjects"][projectID]["updated"]
                outDict["details"] = request.session["currentProjects"][projectID]["details"]
                outDict["processes"] = []
                for elem in request.session["currentProjects"][projectID]["processes"]:
                    outDict["processes"].append(request.session["currentProjects"][projectID]["processes"][elem])
                return JsonResponse(outDict)
        
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, getProject.__name__):
            return JsonResponse(pgProcesses.ProcessManagementBase.getProject(projectID, pgProfiles.ProfileManagementBase.getUserHashID(request.session), pgProfiles.ProfileManagementBase.getOrgaHashID(request.session)))

        return JsonResponse(outDict)
    except (Exception) as error:
        logger.error(f"getProject: {str(error)}")

    return JsonResponse({})

#######################################################
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=True)
def retrieveProjects(request):
    """
    Retrieve all saved projects with processes.

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response with projects/processes of that user
    :rtype: JSON Response

    """

    return JsonResponse(pgProcesses.processManagement[request.session["pgProcessClass"]].getProjects(request.session), safe=False)
    

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
    lastLogin = user["lastSeen"]
    projects = pgProcesses.processManagement[request.session["pgProcessClass"]].getProjects(request.session)

    output = {"eventType": "projectEvent", "events": []}

    for project in projects:
        currentProject = {}
        currentProject["projectID"] = project["projectID"]
        processArray = []
        for process in project["processes"]:
            currentProcess = {}
            currentProcess["processID"] = process["processID"]
            newMessagesCount = 0
            chat = process["messages"]["messages"]
            for messages in chat:
                if lastLogin < timezone.make_aware(datetime.strptime(messages["date"], '%Y-%m-%dT%H:%M:%S.%fZ')) and messages["userID"] != user["hashedID"]:
                    newMessagesCount += 1
            if lastLogin < timezone.make_aware(datetime.strptime(process["updated"], '%Y-%m-%d %H:%M:%S.%f+00:00')):
                status = 1
            else:
                status = 0
            
            # if something changed, save it. If not, discard
            if status !=0 or newMessagesCount != 0: 
                currentProcess["status"] = status
                currentProcess["messages"] = newMessagesCount

                processArray.append(currentProcess)
        if len(processArray):
            currentProject["processes"] = processArray
            output["events"].append(currentProject)
    
    # set accessed time to now
    pgProfiles.ProfileManagementBase.setLoginTime(user["hashedID"])

    return JsonResponse(output, status=200, safe=False)

################################################################################################
# Save, verify, send

##############################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def getContractors(request):
    """
    Get all suitable manufacturers.

    :param request: GET request
    :type request: HTTP GET
    :return: List of manufacturers and some details
    :rtype: JSON

    """
    # TODO filter by service
    manufacturerList = []
    listOfAllManufacturers = pgProfiles.ProfileManagementOrganization.getAllContractors()
    # TODO Check suitability

    # remove unnecessary information and add identifier
    for idx, elem in enumerate(listOfAllManufacturers):
        manufacturerList.append({})
        manufacturerList[idx]["name"] = elem["name"]
        manufacturerList[idx]["id"] = elem["hashedID"]

    return JsonResponse(manufacturerList, safe=False)

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
        if manualCheckifLoggedIn(session) and manualCheckIfRightsAreSufficient(session, "saveProjects"):
            if session["isPartOfOrganization"]:
                error = pgProcesses.ProcessManagementOrganization.addProjectToDatabase(session)
            else:
                error = pgProcesses.ProcessManagementUser.addProjectToDatabase(session)
            if isinstance(error, Exception):
                raise error
            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(session)},{Logging.Predicate.PREDICATE},saved,{Logging.Object.OBJECT},their projects," + str(datetime.now()))
        return None
    
    except (Exception) as error:
        logger.error(f"saveProjectsViaWebsocket: {str(error)}")
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
        # TODO Save picture and files in permanent storage, and change "files" field to urls

        if request.session["isPartOfOrganization"]:
            error = pgProcesses.ProcessManagementOrganization.addProjectToDatabase(request.session)
        else:
            error = pgProcesses.ProcessManagementUser.addProjectToDatabase(request.session)
        if isinstance(error, Exception):
            raise error

        request.session["currentProjects"].clear()
        del request.session["currentProjects"]
        request.session.modified = True

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.PREDICATE},saved,{Logging.Object.OBJECT},their projects," + str(datetime.now()))
        return HttpResponse("Success")
    
    except (Exception) as error:
        logger.error(f"saveProjects: {str(error)}")
        return HttpResponse("Failed")
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"]) 
@checkIfRightsAreSufficient(json=False)
def verifyProject(request):
    """
    Start calculations on server and set status accordingly

    :param request: GET Request
    :type request: HTTP GET
    :return: Response if processes are started successfully
    :rtype: HTTP Response

    """
    try:
        # get information
        info = json.loads(request.body.decode("utf-8"))
        projectID = info["projectID"]
        sendToManufacturerAfterVerification = info["send"]
        processesIDArray = info["processIDs"]

        # first save projects
        if "currentProjects" in request.session:
            if request.session["isPartOfOrganization"]:
                error = pgProcesses.ProcessManagementOrganization.addProjectToDatabase(request.session)
            else:
                error = pgProcesses.ProcessManagementUser.addProjectToDatabase(request.session)
            if isinstance(error, Exception):
                raise error

            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.PREDICATE},saved,{Logging.Object.OBJECT},their projects," + str(datetime.now()))
            
            # then clear drafts from session
            
            request.session["currentProjects"].clear()
            del request.session["currentProjects"]


        # TODO start services and set status to "verifying" instead of verified
        #listOfCallIDsAndProcessesIDs = []
        for entry in processesIDArray:
            pgProcesses.ProcessManagementBase.updateProcess(entry, pgProcesses.EnumUpdates.status, ProcessStatus.getStatusCodeFor("VERIFIED"))
            #call = price.calculatePrice_Mock.delay([1,2,3]) # placeholder for each thing like model, material, post-processing
            #listOfCallIDsAndProcessesIDs.append((call.id, entry, collectAndSend.EnumResultType.price))

        # start collecting process, 
        #collectAndSend.waitForResultAndSendProcess(listOfCallIDsAndProcessesIDs, sendToManufacturerAfterVerification)

        # TODO Websocket Event

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.PREDICATE},verify,{Logging.Object.OBJECT},process {projectID}," + str(datetime.now()))

        if sendToManufacturerAfterVerification:
            sendProject(request)

        return HttpResponse("Success")
    
    except (Exception) as error:
        logger.error(f"verifyProject: {str(error)}")
        return HttpResponse("Failed")
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"]) 
@checkIfRightsAreSufficient(json=False)
def sendProject(request):
    """
    Retrieve Calculations and send process to manufacturer(s)

    :param request: GET Request
    :type request: HTTP GET
    :return: Response if processes are started successfully
    :rtype: HTTP Response

    """
    try:
        info = json.loads(request.body.decode("utf-8"))
        projectID = info["projectID"]
        processesIDArray = info["processIDs"]
        # TODO Check if process is verified

        for entry in processesIDArray:
            pgProcesses.ProcessManagementBase.updateProcess(entry, pgProcesses.EnumUpdates.status, ProcessStatus.getStatusCodeFor("REQUESTED"))
            pgProcesses.ProcessManagementBase.sendProcess(entry)

            
        # TODO Websocket Events
        dictForEvents = pgProcesses.ProcessManagementBase.getInfoAboutProjectForWebsocket(projectID, processesIDArray, "status")
        channel_layer = get_channel_layer()
        for userID in dictForEvents: # user/orga that is associated with that process
            values = dictForEvents[userID] # message, formatted for frontend
            subID = pgProfiles.ProfileManagementBase.getUserKeyViaHash(userID) # primary key
            if subID != pgProfiles.ProfileManagementBase.getUserKey(session=request.session): # don't show a message for the user that changed it
                userKeyWOSC = pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=subID)
                for permission in rights.rightsManagement.getPermissionsNeededForPath(sendProject.__name__):
                    async_to_sync(channel_layer.group_send)(userKeyWOSC+permission, {
                        "type": "sendMessageJSON",
                        "dict": values,
                    })


        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.PREDICATE},sent,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))
        
        return HttpResponse("Success")
    
    except (Exception) as error:
        logger.error(f"sendProject: {str(error)}")
        return HttpResponse("Failed")


