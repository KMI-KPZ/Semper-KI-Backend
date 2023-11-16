"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling of database requests
"""

import datetime
import json, logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from ..utilities import basics

from ..connections.postgresql import pgProfiles

logger = logging.getLogger("logToFile")
##############################################
# @checkIfUserIsLoggedIn()
# @require_http_methods(["GET"])
# def addUserTest(request):
#     """
#     Same as addUser but for testing.

#     :param request: GET request
#     :type request: HTTP GET
#     :return: HTTP response
#     :rtype: HTTP status

#     """

#     flag = request.session["pgProfileClass"].addUserIfNotExists(request.session)
#     if flag is True:
#         return HttpResponse("Worked")
#     else:
#         return HttpResponse("Failed", status=500)


##############################################
# @checkIfUserIsLoggedIn()
# @require_http_methods(["GET"])
# def getUserTest(request):
#     """
#     Same as getUser but for testing.

#     :param request: GET request
#     :type request: HTTP GET
#     :return: User details from database
#     :rtype: JSON

#     """
#     return JsonResponse(pgProfiles.ProfileManagement.getUser(request.session))

#######################################################
@basics.checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
def getOrganizationDetails(request):
    """
    Return details about organization. 

    :param request: GET request
    :type request: HTTP GET
    :return: Organization details
    :rtype: Json

    """
    # Read organization details from Database
    return JsonResponse(pgProfiles.ProfileManagementBase.getOrganization(request.session))

##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"])
@basics.checkIfRightsAreSufficient()
def updateDetailsOfOrganization(request):
    """
    Update details of organization of that user.

    :param request: PATCH request
    :type request: HTTP PATCH
    :return: HTTP response
    :rtype: HTTP status

    """

    content = json.loads(request.body.decode("utf-8"))["data"]["content"]
    logger.info(f"{basics.Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{basics.Logging.Predicate.EDITED},updated,{basics.Logging.Object.ORGANISATION},details of {pgProfiles.ProfileManagementOrganization.getOrganization(request.session)['name']}," + str(datetime.datetime.now()))
    flag = pgProfiles.ProfileManagementOrganization.updateContent(request.session, content)
    if flag is True:
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)

##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["DELETE"])
@basics.checkIfRightsAreSufficient()
def deleteOrganization(request):
    """
    Deletes an entry in the database corresponding to user name.

    :param request: DELETE request
    :type request: HTTP DELETE
    :return: HTTP response
    :rtype: HTTP status

    """
    logger.info(f"{basics.Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{basics.Logging.Predicate.DELETED},deleted,{basics.Logging.Object.ORGANISATION},organization {pgProfiles.ProfileManagementOrganization.getOrganization(request.session)['name']}," + str(datetime.datetime.now()))
    flag = pgProfiles.ProfileManagementBase.deleteOrganization(request.session)
    if flag is True:
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)

#######################################################
@basics.checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
def getUserDetails(request):
    """
    Return details about user. 

    :param request: GET request
    :type request: HTTP GET
    :return: User details
    :rtype: Json

    """
    # Read user details from Database
    userObj = pgProfiles.ProfileManagementBase.getUser(request.session)
    userObj["usertype"] = request.session["usertype"]
    return JsonResponse(userObj)

##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"])
def updateDetails(request):
    """
    Update user details.

    :param request: PATCH request
    :type request: HTTP PATCH
    :return: HTTP response
    :rtype: HTTP status

    """

    content = json.loads(request.body.decode("utf-8"))
    logger.info(f"{basics.Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{basics.Logging.Predicate.EDITED},updated,{basics.Logging.Object.SELF},details," + str(datetime.datetime.now()))
    flag = pgProfiles.ProfileManagementUser.updateContent(request.session, content)
    if flag is True:
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)
    

##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["DELETE"])
def deleteUser(request):
    """
    Deletes an entry in the database corresponding to user name.

    :param request: DELETE request
    :type request: HTTP DELETE
    :return: HTTP response
    :rtype: HTTP status

    """
    logger.info(f"{basics.Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{basics.Logging.Predicate.DELETED},deleted,{basics.Logging.Object.SELF},," + str(datetime.datetime.now()))
    flag = pgProfiles.ProfileManagementUser.deleteUser(request.session)
    if flag is True:
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)
