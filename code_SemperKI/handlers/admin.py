"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling of admin view requests

"""

import datetime, json, logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from code_General.utilities import basics
from ..connections.postgresql import pgProcesses
from code_General.connections.postgresql import pgProfiles

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
        clientID = entry["client"]
        userName = pgProfiles.ProfileManagementBase.getUserNameViaHash(clientID)
        projects[idx]["clientName"] = userName
        
    logger.info(f"{basics.Logging.Subject.ADMIN},{request.session['user']['userinfo']['nickname']},{basics.Logging.Predicate.FETCHED},fetched,{basics.Logging.Object.SYSTEM},projects," + str(datetime.datetime.now()))
    return JsonResponse(projects, safe=False)

##############################################
@basics.checkIfUserIsLoggedIn(json=True)
@basics.checkIfUserIsAdmin(json=True)
@require_http_methods(["GET"])
def getSpecificProjectAsAdmin(request, projectID):
    """
    Get all processes for specific project.

    :param request: GET request
    :type request: HTTP GET
    :param projectID: Project for which details are necessary
    :type projectID: str
    :return: JSON response, list
    :rtype: JSONResponse
    """
    processes = pgProcesses.ProcessManagementBase.getProcessesPerPID(projectID)
    for idx, entry in enumerate(processes):
        clientID = entry["client"]
        userName = pgProfiles.ProfileManagementBase.getUserNameViaHash(clientID)
        processes[idx]["clientName"] = userName
        
        processes[idx]["contractorNames"] = []
        for contractorID in entry["contractor"]:
            contractorName = pgProfiles.ProfileManagementBase.getUserNameViaHash(contractorID)
            processes[idx]["contractorNames"].append(contractorName)

    logger.info(f"{basics.Logging.Subject.ADMIN},{request.session['user']['userinfo']['nickname']},{basics.Logging.Predicate.FETCHED},fetched,{basics.Logging.Object.SYSTEM},processes from {projectID}," + str(datetime.datetime.now()))
    return JsonResponse(processes, safe=False)