"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling of admin view requests

"""

import datetime, json, logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from Generic_Backend.code_General.utilities import basics
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from ..connections.content.postgresql import pgProcesses
from ..definitions import ProcessDescription

logger = logging.getLogger("logToFile")

# Projects #############################################################################################################

##############################################
@basics.checkIfUserIsLoggedIn(json=True)
@basics.checkIfUserIsAdmin(json=True)
@require_http_methods(["GET"])
def getAllProjectsFlatAsAdmin(request):
    """
    Get all Projects in flat format.

    :param request: GET request
    :type request: HTTP GET
    :return: JSON response
    :rtype: JSONResponse
    """
    # get all projects if you're an admin
    projects = pgProcesses.ProcessManagementBase.getAllProjectsFlat()
    for idx, entry in enumerate(projects):
        clientID = entry[ProcessDescription.client]
        userName = pgProfiles.ProfileManagementBase.getUserNameViaHash(clientID)
        projects[idx]["clientName"] = userName
        
    logger.info(f"{basics.Logging.Subject.ADMIN},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{basics.Logging.Predicate.FETCHED},fetched,{basics.Logging.Object.SYSTEM},all projects," + str(datetime.datetime.now()))
    return JsonResponse(projects, safe=False)

##############################################
@basics.checkIfUserIsLoggedIn(json=True)
@basics.checkIfUserIsAdmin(json=True)
@require_http_methods(["GET"])
def getSpecificProjectAsAdmin(request, projectID):
    """
    Get all info for a specific project.

    :param request: GET request
    :type request: HTTP GET
    :param projectID: Project for which details are necessary
    :type projectID: str
    :return: JSON response
    :rtype: JSONResponse
    """

    logger.info(f"{basics.Logging.Subject.ADMIN},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{basics.Logging.Predicate.FETCHED},fetched,{basics.Logging.Object.SYSTEM},project {projectID}," + str(datetime.datetime.now()))
    return JsonResponse(pgProcesses.ProcessManagementBase.getProject(projectID))

    