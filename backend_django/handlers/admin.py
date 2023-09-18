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

from ..handlers import basics
from ..services.postgresDB import pgProfiles, pgOrders

logger = logging.getLogger(__name__)

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
    logger.info(f"Admin {request.session['user']['userinfo']['nickname']} fetched all users and orgas at " + str(datetime.datetime.now()))
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
    logger.info(f"Admin {request.session['user']['userinfo']['nickname']} updated details of {userName} at " + str(datetime.datetime.now()))
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
    logger.info(f"Admin {request.session['user']['userinfo']['nickname']} updated details of organization {orgaName} at " + str(datetime.datetime.now()))
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
        logger.info(f"Admin {request.session['user']['userinfo']['nickname']} deleted organization {orgaName} at " + str(datetime.datetime.now()))
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
        logger.info(f"Admin {request.session['user']['userinfo']['nickname']} deleted {userName} at " + str(datetime.datetime.now()))
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)
    
# Orders #############################################################################################################

##############################################
@basics.checkIfUserIsLoggedIn(json=True)
@basics.checkIfUserIsAdmin(json=True)
@require_http_methods(["GET"])
def getAllOrdersFlatAsAdmin(request):
    """
    Get all Orders in flat format.

    :param request: GET request
    :type request: HTTP GET
    :return: JSON response
    :rtype: JSONResponse
    """
    # get all orders if you're an admin
    orderCollections = pgOrders.OrderManagementBase.getAllOCsFlat()
    for entry in orderCollections:
        clientID = orderCollections[entry]["client"]
        userObj = pgProfiles.ProfileManagementBase.getUserViaHash(clientID)
        orderCollections[entry]["clientName"] = userObj.name
        
    logger.info(f"Admin {request.session['user']['userinfo']['nickname']} fetched all orders at " + str(datetime.datetime.now()))
    return JsonResponse(orderCollections, safe=False)

##############################################
@basics.checkIfUserIsLoggedIn(json=True)
@basics.checkIfUserIsAdmin(json=True)
@require_http_methods(["GET"])
def getSpecificOrderAsAdmin(request, orderCollectionID):
    """
    Get all orders for specific order collection.

    :param request: GET request
    :type request: HTTP GET
    :param orderCollectionID: Order for which details are necessary
    :type orderCollectionID: str
    :return: JSON response, list
    :rtype: JSONResponse
    """
    orders = pgOrders.OrderManagementBase.getOrderPerOCID(orderCollectionID)
    for idx, entry in enumerate(orders):
        clientID = entry["client"]
        userObj = pgProfiles.ProfileManagementBase.getUserViaHash(clientID)
        orders[idx]["clientName"] = userObj.name
        
        orders[idx]["contractorNames"] = []
        for contractorID in entry["contractor"]:
            contractorObj = pgProfiles.ProfileManagementBase.getUserViaHash(contractorID)
            orders[idx]["contractorNames"].append(contractorObj.name)

    
    logger.info(f"Admin {request.session['user']['userinfo']['nickname']} fetched all subOrders from {orderCollectionID} at " + str(datetime.datetime.now()))
    return JsonResponse(orders, safe=False)