"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logic for the projects
"""
import logging, numpy

from datetime import datetime
from django.utils import timezone

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import manualCheckIfRightsAreSufficient, manualCheckifLoggedIn

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.definitions import *
from code_SemperKI.states.states import getFlatStatus

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
def logicForGetProjectForDashboard(request, projectID) -> tuple[dict|Exception, int]:
    """
    Get the full project

    :return: The project
    :rtype: tuple[dict, int]
    """

    contentManager = ManageContent(request.session)
    interface = contentManager.getCorrectInterface("getProjectForDashboard")
    if interface == None:
        return (Exception("Rights not sufficient in getProjectForDashboard"), 401)
    
    
    projectAsDict = interface.getProject(projectID)
    if isinstance(projectAsDict, Exception):
        return (Exception("Project not found in getProjectForDashboard"), 404)
        
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

            listOfFlatProcesses.append(entry)

    projectAsDict[SessionContentSemperKI.processes] = listOfFlatProcesses
    return (projectAsDict, 200)
