"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers for the dashboard
"""

import json, random, logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ..handlers.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient

from ..services import postgres

logger = logging.getLogger(__name__)
#######################################################
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient("retrieveOrders", json=True)
def retrieveOrders(request):
    """
    TODO
    Retrieve saved orders for dashboard.

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response with orders of that user
    :rtype: JSON Response

    """
    uID = postgres.ProfileManagement.getUserHashID(request.session)
    return JsonResponse(postgres.OrderManagement.getOrders(uID), safe=False)
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["PUT"])
@checkIfRightsAreSufficient("updateOrder", json=False)
def updateOrder(request):
    """
    TODO
    Update saved orders for dashboard.

    :param request: PUT Request
    :type request: HTTP PUT
    :return: HTTP Response if update worked
    :rtype: HTTP Response

    """

    content = json.loads(request.body.decode("utf-8"))
    if "props" in content:
        orderID = ""
        orderCollectionID = ""
        if "orderID" in content["props"]:
            orderID = content["props"]["orderID"]
        if "orderCollectionID" in content["props"]:
            orderCollectionID = content["props"]["orderCollectionID"]

        outputDict = {"eventType": "orderEvent"}
        outputDict["orderCollectionID"] = orderCollectionID

        if "chat" in content["props"]:
            postgres.OrderManagement.updateOrder(orderID, orderCollectionID, postgres.EnumUpdates.chat, content["props"]["chat"])
            outputDict["orders"] = [{"orderID": orderID, "status": 0, "messages": 1}]

        if "state" in content["props"]:
            postgres.OrderManagement.updateOrder(orderID, orderCollectionID, postgres.EnumUpdates.status, content["props"]["state"])
            outputDict["orders"] = [{"orderID": orderID, "status": 1, "messages": 0}]

        # send to websockets that are active, that a new message/status is available for that order
        channel_layer = get_channel_layer()
        listOfUsers = postgres.OrderManagement.getAllUsersOfOrder(orderID)
        for user in listOfUsers:
            if user.subID != postgres.ProfileManagement.getUserKey(session=request.session):
                async_to_sync(channel_layer.group_send)(postgres.ProfileManagement.getUserKeyWOSC(uID=user.subID), {
                    "type": "sendMessageJSON",
                    "dict": outputDict,
                })
    logger.info(f"{postgres.ProfileManagement.getUser(request.session)['name']} updated order {orderID} at " + str(datetime.now()))
    return HttpResponse("Success")

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["DELETE"])
@checkIfRightsAreSufficient("deleteOrder", json=False)
def deleteOrder(request):
    """
    Delete a specific order.

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: HTTP Response if update worked
    :rtype: HTTP Response

    """

    content = json.loads(request.body.decode("utf-8"))
    if postgres.OrderManagement.deleteOrder(content["id"]):
        logger.info(f"{postgres.ProfileManagement.getUser(request.session)['name']} deleted order {content['id']} at " + str(datetime.now()))
        return HttpResponse("Success")
    else:
        return HttpResponse("Failed")

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["DELETE"])
@checkIfRightsAreSufficient("deleteOrderCollection", json=False)
def deleteOrderCollection(request):
    """
    Delete a specific order collection.

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: HTTP Response if update worked
    :rtype: HTTP Response

    """
    content = json.loads(request.body.decode("utf-8"))
    if postgres.OrderManagement.deleteOrderCollection(content["id"]):
        logger.info(f"{postgres.ProfileManagement.getUser(request.session)['name']} deleted orderCollection {content['id']} at " + str(datetime.now()))
        return HttpResponse("Success")
    else:
        return HttpResponse("Failed")
    

#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
@checkIfRightsAreSufficient("getMissedEvents", json=True)
def getMissedEvents(request):
    """
    TODO
    Show how many events (chat messages ...) were missed since last login.

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response with numbers for every order and orderCollection
    :rtype: JSON Response

    """

    user = postgres.ProfileManagement.getUser(request.session)
    lastLogin = user["lastSeen"]
    orderCollections = postgres.OrderManagement.getOrders(user["hashedID"])

    output = {"eventType": "orderEvent", "events": []}

    for orderCollection in orderCollections:
        currentCollection = {}
        currentCollection["orderCollectionID"] = orderCollection["id"]
        orderArray = []
        for orders in orderCollection["orders"]:
            currentOrder = {}
            currentOrder["orderID"] = orders["id"]
            newMessagesCount = 0
            chat = orders["chat"]["messages"]
            for messages in chat:
                if lastLogin < timezone.make_aware(datetime.strptime(messages["date"], '%Y-%m-%dT%H:%M:%S.%fZ')) and messages["userID"] != user["hashedID"]:
                    newMessagesCount += 1
            if lastLogin < orders["updatedWhen"]:
                status = 1
            else:
                status = 0
            
            # if something changed, save it. If not, discard
            if status !=0 or newMessagesCount != 0: 
                currentOrder["status"] = status
                currentOrder["messages"] = newMessagesCount

                orderArray.append(currentOrder)
        if len(orderArray):
            currentCollection["orders"] = orderArray
            output["events"].append(currentCollection)
    
    # set accessed time to now
    postgres.ProfileManagement.setLoginTime(user["hashedID"])

    return JsonResponse(output, status=200, safe=False)


