"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling of admin view requests

"""

import datetime, json, logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ..utilities import basics
from ..services.postgresDB import pgProcesses, pgProfiles

logger = logging.getLogger("logToFile")

# Profiles #############################################################################################################

##############################################
@basics.checkIfUserIsLoggedIn(json=True)
@basics.checkIfUserIsAdmin(json=True)
@require_http_methods(["GET"])
def getAllAsAdmin(request):
    """
    Drop all information (of the DB) about all users for admin view.

    :param request: GET request
    :type request: HTTP GET
    :return: JSON response containing all entries of users
    :rtype: JSON Respone

    """
    # get all information if you're an admin
    users, organizations = pgProfiles.ProfileManagementBase.getAll()
    outLists = { "user" : users, "organizations": organizations }
    logger.info(f"{basics.Logging.Subject.ADMIN},{request.session['user']['userinfo']['nickname']},{basics.Logging.Predicate.FETCHED},fetched,{basics.Logging.Object.SYSTEM}, all users and orgas," + str(datetime.datetime.now()))
    return JsonResponse(outLists, safe=False)

##############################################
@basics.checkIfUserIsLoggedIn()
@basics.checkIfUserIsAdmin()
@require_http_methods(["PATCH"])
def updateDetailsOfUserAsAdmin(request):
    """
    Update user details.

    :param request: PATCH request
    :type request: HTTP PATCH
    :return: HTTP response
    :rtype: HTTP status

    """
    content = json.loads(request.body.decode("utf-8"))
    userHasedID = content["hashedID"]
    userID = pgProfiles.ProfileManagementBase.getUserKeyViaHash(userHasedID)
    userName = content["name"]
    logger.info(f"{basics.Logging.Subject.ADMIN},{request.session['user']['userinfo']['nickname']},{basics.Logging.Predicate.EDITED},updated,{basics.Logging.Object.USER},{userID}," + str(datetime.datetime.now()))
    flag = pgProfiles.ProfileManagementUser.updateContent(request.session, content, userID)
    if flag is True:
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)
    
##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"])
@basics.checkIfRightsAreSufficient()
def updateDetailsOfOrganizationAsAdmin(request):
    """
    Update details of organization of that user.

    :param request: PATCH request
    :type request: HTTP PATCH
    :return: HTTP response
    :rtype: HTTP status

    """

    content = json.loads(request.body.decode("utf-8"))["data"]["content"]
    orgaHasedID = content["hashedID"]
    orgaID = pgProfiles.ProfileManagementBase.getUserKeyViaHash(orgaHasedID)
    orgaName = content["name"]
    logger.info(f"{basics.Logging.Subject.ADMIN},{request.session['user']['userinfo']['nickname']},{basics.Logging.Predicate.EDITED},updated,{basics.Logging.Object.ORGANISATION},{orgaID}," + str(datetime.datetime.now()))
    flag = pgProfiles.ProfileManagementOrganization.updateContent(request.session, content, orgaID)
    if flag is True:
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)

##############################################
@basics.checkIfUserIsLoggedIn()
@basics.checkIfUserIsAdmin()
@require_http_methods(["DELETE"])
def deleteOrganizationAsAdmin(request):
    """
    Deletes an entry in the database corresponding to orga id.

    :param request: DELETE request
    :type request: HTTP DELETE
    :return: HTTP response
    :rtype: HTTP status

    """
    content = json.loads(request.body.decode("utf-8"))
    orgaID = content["hashedID"]
    orgaName = content["name"]

    flag = pgProfiles.ProfileManagementBase.deleteOrganization(request.session, orgaID)
    if flag is True:
        logger.info(f"{basics.Logging.Subject.ADMIN},{request.session['user']['userinfo']['nickname']},{basics.Logging.Predicate.DELETED},deleted,{basics.Logging.Object.ORGANISATION},{orgaID}," + str(datetime.datetime.now()))
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)

##############################################
@basics.checkIfUserIsLoggedIn()
@basics.checkIfUserIsAdmin()
@require_http_methods(["DELETE"])
def deleteUserAsAdmin(request):
    """
    Deletes an entry in the database corresponding to user id.

    :param request: DELETE request
    :type request: HTTP DELETE
    :return: HTTP response
    :rtype: HTTP status

    """
    content = json.loads(request.body.decode("utf-8"))
    userHasedID = content["hashedID"]
    userID = pgProfiles.ProfileManagementBase.getUserKeyViaHash(userHasedID)
    userName = content["name"]
    # websocket event for that user
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=userID), {
            "type": "sendMessageJSON",
            "dict": {"eventType": "accountEvent", "context": "deleteUser"},
        })

    flag = pgProfiles.ProfileManagementUser.deleteUser(request.session, userHasedID)
    if flag is True:
        logger.info(f"{basics.Logging.Subject.ADMIN},{request.session['user']['userinfo']['nickname']},{basics.Logging.Predicate.DELETED},deleted,{basics.Logging.Object.USER},{userID}," + str(datetime.datetime.now()))
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)
    
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
    projects = pgProcesses.ProcessManagementBase.getAllPsFlat()
    for idx, entry in enumerate(projects):
        clientID = entry["client"]
        userObj = pgProfiles.ProfileManagementBase.getUserViaHash(clientID)
        projects[idx]["clientName"] = userObj.name
        
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
        userObj = pgProfiles.ProfileManagementBase.getUserViaHash(clientID)
        processes[idx]["clientName"] = userObj.name
        
        processes[idx]["contractorNames"] = []
        for contractorID in entry["contractor"]:
            contractorObj = pgProfiles.ProfileManagementBase.getUserViaHash(contractorID)
            processes[idx]["contractorNames"].append(contractorObj.name)

    logger.info(f"{basics.Logging.Subject.ADMIN},{request.session['user']['userinfo']['nickname']},{basics.Logging.Predicate.FETCHED},fetched,{basics.Logging.Object.SYSTEM},processes from {projectID}," + str(datetime.datetime.now()))
    return JsonResponse(processes, safe=False)