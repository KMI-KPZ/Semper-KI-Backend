"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logic for the projects
"""
import logging, numpy

from datetime import datetime
from django.utils import timezone
from django.conf import settings

from rest_framework import status

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.utilities.basics import manualCheckIfRightsAreSufficient, manualCheckifLoggedIn, manualCheckifAdmin

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.definitions import *
from code_SemperKI.states.stateDescriptions import ButtonLabels
from code_SemperKI.states.states import getButtonsForProcess, getFlatStatus, getMissingElements
from code_SemperKI.logics.processLogics import parseProcessOutputForFrontend

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
####################################################################################

##################################################
def logicForGetFlatProjects(request) -> tuple[dict|Exception, int]:
    """
    Get the projects for the dashboard

    :return: The projects or Exception and status code
    :rtype: dict|Exception, int
    """
    try:
        outDict = {"projects": []}
        contentManager = ManageContent(request.session)

        # Gather from session...
        if contentManager.sessionManagement.getIfContentIsInSession():
            sessionContent = contentManager.sessionManagement.getProjectsFlat(request.session)
            outDict["projects"].extend(sessionContent)
        
        # ... and from database
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, "getFlatProjects"):           
            objFromDB = contentManager.postgresManagement.getProjectsFlat(request.session)
            if len(objFromDB) >= 1:
                outDict["projects"].extend(objFromDB)

        outDict["projects"] = sorted(outDict["projects"], key=lambda x: 
                timezone.make_aware(datetime.strptime(x[ProjectDescription.createdWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
        
        return (outDict, 200)
    except Exception as e:
        loggerError.error(f"Error in logicForGetFlatProjects: {str(e)}")
        return (e, 500)
    
##################################################
def logicForGetProjectForDashboard(request, projectID:str, functionName:str) -> tuple[dict|Exception, int]:
    """
    Get the full project

    :param request: The request
    :type request: WSGIRequest
    :param projectID: The project ID
    :type projectID: str
    :param functionName: The name of the function
    :type functionName: str
    :return: The project
    :rtype: tuple[dict, int]
    """
    try:    
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(functionName)
        if interface == None:
            return (Exception(f"Rights not sufficient in {functionName}"), 401)
        
        projectAsDict = interface.getProject(projectID)
        if isinstance(projectAsDict, Exception):
            return (Exception(f"Project not found in {functionName}"), 404)
            
        processList = projectAsDict[SessionContentSemperKI.processes]
        listOfFlatProcesses = []
        if manualCheckifLoggedIn(request.session):
            if pgProfiles.ProfileManagementBase.checkIfUserIsInOrganization(request.session):
                currentUserID = pgProfiles.ProfileManagementBase.getOrganizationHashID(request.session)
            else:
                currentUserID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
        else:
            currentUserID = GlobalDefaults.anonymous
        
        for entry in processList:
            # list only processes that either the user or the receiving organization should see

            if entry[ProcessDescription.client] == currentUserID or \
                ( ProcessDescription.contractor in entry and \
                len(entry[ProcessDescription.contractor]) != 0 and \
                    entry[ProcessDescription.contractor][OrganizationDescription.hashedID] == currentUserID):

                processObj = interface.getProcessObj(projectID, entry[ProcessDescription.processID])
                retVal, statusCode = parseProcessOutputForFrontend(processObj, contentManager, functionName)
                if statusCode != 200:
                    return (retVal, statusCode)
            
                listOfFlatProcesses.append(retVal)

        projectAsDict[SessionContentSemperKI.processes] = listOfFlatProcesses
        return (projectAsDict, 200)
    except Exception as e:
        loggerError.error(f"Error in logicForGetProjectForDashboard: {str(e)}")
        return (e, 500)

##################################################
def logicForGetProject(request, projectID:str, functionName:str):
    """
    Get the full project but with flat processes

    :param request: The request
    :type request: WSGIRequest
    :param projectID: The project ID
    :type projectID: str
    :param functionName: The name of the function
    :type functionName: str
    :return: The project
    :rtype: tuple[dict, int]
    
    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(functionName)
        if interface == None:
            return Exception(f"Rights not sufficient in {functionName}"), status.HTTP_401_UNAUTHORIZED

        projectAsDict = interface.getProject(projectID)
        if isinstance(projectAsDict, Exception):
            return Exception(f"Project not found in {functionName}"), status.HTTP_404_NOT_FOUND

        processList = projectAsDict[SessionContentSemperKI.processes]
        listOfFlatProcesses = []
        if manualCheckifLoggedIn(request.session):
            if pgProfiles.ProfileManagementBase.checkIfUserIsInOrganization(request.session):
                currentUserID = pgProfiles.ProfileManagementBase.getOrganizationHashID(request.session)
            else:
                currentUserID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
        else:
            currentUserID = GlobalDefaults.anonymous
        
        for entry in processList:
            # list only processes that either the user or the receiving organization should see

            if entry[ProcessDescription.client] == currentUserID or \
                ( ProcessDescription.contractor in entry and \
                 len(entry[ProcessDescription.contractor]) != 0 and \
                    entry[ProcessDescription.contractor][OrganizationDescription.hashedID] == currentUserID):
                processObj = interface.getProcessObj(projectID, entry[ProcessDescription.processID])
                retVal, statusCode = parseProcessOutputForFrontend(processObj, contentManager, functionName)
                if statusCode != 200:
                    return (retVal, statusCode)
                
                listOfFlatProcesses.append(retVal)

        projectAsDict[SessionContentSemperKI.processes] = listOfFlatProcesses

        return (projectAsDict, 200)
    except Exception as e:
        loggerError.error(f"Error in logicForGetProject: {str(e)}")
        return (e, 500)

##################################################
def logicForCreateProjectID(request, validatedInput:dict, functionName:str):
    """
    Create a project and return its ID

    :param request: The request
    :type request: WSGIRequest
    :param validatedInput: The validated input
    :type validatedInput: dict
    :param functionName: The name of the function
    :type functionName: str
    :return: The project ID
    :rtype: tuple[dict|Exception, int]
    
    """
    try:
        projectTitle = validatedInput[ProjectDetails.title]

        # generate ID string, make timestamp and create template for project
        projectID = crypto.generateURLFriendlyRandomString()
        #now = timezone.now()
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(functionName)
        if interface == None:
            return Exception(f"Rights not sufficient in {functionName}"), status.HTTP_401_UNAUTHORIZED

        client = contentManager.getClient()
        interface.createProject(projectID, client)
        interface.updateProject(projectID, ProjectUpdates.projectDetails, {ProjectDetails.title: projectTitle})

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))

        #return just the id for the frontend
        output = {ProjectDescription.projectID: projectID}
        return (output, 200)
    except Exception as e:
        loggerError.error(f"Error in logicForCreateProjectID: {str(e)}")
        return (e, 500)

##################################################
def logicForUpdateProject(request, validatedInput:dict, functionName:str):
    """
    Update a project

    :param request: The request
    :type request: WSGIRequest
    :param validatedInput: The validated input
    :type validatedInput: dict
    :param functionName: The name of the function
    :type functionName: str
    :return: Nothing or exception
    :rtype: tuple[None|Exception, int]
    
    """
    try:
        projectID = validatedInput[ProjectDescription.projectID]

        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(functionName)
        if interface == None or not contentManager.checkRightsForProject(projectID):
            return Exception(f"Rights not sufficient in {functionName}"), status.HTTP_401_UNAUTHORIZED

        for entry in validatedInput["changes"]:
            returnVal = interface.updateProject(projectID, entry, validatedInput["changes"][entry])
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

        return None, 200
    except Exception as e:
        loggerError.error(f"Error in logicForUpdateProject: {str(e)}")
        return (e, 500)

##################################################
def logicForDeleteProjects(request, functionName:str):
    """
    Delete projects

    :param request: The request
    :type request: WSGIRequest
    :param functionName: The name of the function
    :type functionName: str
    :return: Nothing or exception
    :rtype: tuple[None|Exception, int]
    
    """
    try:
        projectIDs = request.GET['projectIDs'].split(",")
        #loggedIn = False # don't check rights in every iteration

        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(functionName)
        if interface is None:
            return Exception(f"Rights not sufficient in {functionName}"), status.HTTP_401_UNAUTHORIZED

        adminOrNot = manualCheckifAdmin(contentManager.currentSession)
        clientID = contentManager.getClient()

        for projectID in projectIDs:
            if not contentManager.checkRightsForProject(projectID):
                return Exception(f"Rights not sufficient in {functionName}"), status.HTTP_401_UNAUTHORIZED
            
            # check if at least one process is "too far gone"
            processes = interface.getProject(projectID)[SessionContentSemperKI.processes]
            if len(processes) > 0:
                for process in processes:
                    contractor = False
                    if process[ProcessDescription.contractor] is not None and process[ProcessDescription.contractor] != {}:
                        contractor = process[ProcessDescription.contractor][OrganizationDescription.hashedID] == clientID
                    buttons = getButtonsForProcess(interface, interface.getProcessObj(projectID, process[ProcessDescription.processID]), process[ProcessDescription.client] == clientID, contractor, adminOrNot) # calls current node of the state machine
                    deletable = False
                    for button in buttons:
                        if button["title"] == ButtonLabels.DELETE_PROCESS.value and button["active"] == True:
                            deletable = True
                            break
                    if not deletable:
                        return Exception(f"Project {projectID} not deletable, process {process[ProcessDescription.processID]} is too far gone"), status.HTTP_401_UNAUTHORIZED

            interface.deleteProject(projectID)
            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))
        
        return None, 200
    except Exception as e:
        loggerError.error(f"Error in logicForDeleteProjects: {str(e)}")
        return (e, 500)

##################################################
def logicForSaveProjects(session):
    """
    Save the projects to the session

    :param session: The session
    :type session: dict
    :return: Nothing
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
    except Exception as e:
        loggerError.error(f"Error in logicForSaveProjects: {str(e)}")
        return e