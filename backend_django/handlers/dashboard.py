"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers for the dashboard
"""

import json, random
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.utils import timezone

from ..handlers.authentification import checkIfUserIsLoggedIn

from ..services import postgres

#######################################################
def retrieveOrders(request):
    """
    Retrieve saved orders for dashboard.

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response with orders of that user
    :rtype: JSON Response

    """
    if checkIfUserIsLoggedIn(request):
        uID = postgres.ProfileManagement.getUserHashID(request.session)
        return JsonResponse(postgres.OrderManagement.getOrders(uID), safe=False)
    else:
        return HttpResponse("Not logged in", status=401)
    
#######################################################
def updateOrder(request):
    """
    Update saved orders for dashboard.

    :param request: POST Request
    :type request: HTTP POST
    :return: HTTP Response if update worked
    :rtype: HTTP Response

    """
    if checkIfUserIsLoggedIn(request):
        if request.method == "PUT":
            content = json.loads(request.body.decode("utf-8"))
            if "props" in content:
                orderID = ""
                orderCollectionID = ""
                if "orderID" in content["props"]:
                    orderID = content["props"]["orderID"]
                if "orderCollectionID" in content["props"]:
                    orderCollectionID = content["props"]["orderCollectionID"]

                if "chat" in content["props"]:
                    postgres.OrderManagement.updateOrder(orderID, orderCollectionID, postgres.EnumUpdates.chat, content["props"]["chat"])
                if "state" in content["props"]:
                    postgres.OrderManagement.updateOrder(orderID, orderCollectionID, postgres.EnumUpdates.status, content["props"]["state"])


        return HttpResponse("Success")
    else:
        return HttpResponse("Not logged in", status=401)
    

#######################################################
def deleteOrder(request):
    """
    Delete a specific order.

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: HTTP Response if update worked
    :rtype: HTTP Response

    """
    if checkIfUserIsLoggedIn(request):
        if request.method == "DELETE":
            content = json.loads(request.body.decode("utf-8"))
            if postgres.OrderManagement.deleteOrder(content["id"]):
                return HttpResponse("Success")
            else:
                return HttpResponse("Failed")
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def deleteOrderCollection(request):
    """
    Delete a specific order collection.

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: HTTP Response if update worked
    :rtype: HTTP Response

    """
    if checkIfUserIsLoggedIn(request):
        if request.method == "DELETE":
            content = json.loads(request.body.decode("utf-8"))
            if postgres.OrderManagement.deleteOrderCollection(content["id"]):
                return HttpResponse("Success")
            else:
                return HttpResponse("Failed")
    else:
        return HttpResponse("Not logged in", status=401)
    

#######################################################
def getMissedEvents(request):
    """
    Show how many events (chat messages ...) were missed since last login.

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response with numbers for every order and orderCollection
    :rtype: JSON Response

    """
    if checkIfUserIsLoggedIn(request):
        user = postgres.ProfileManagement.getUser(request.session)
        lastLogin = user["accessed"]
        orderCollections = postgres.OrderManagement.getOrders(user["hashedID"])

        output = []

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
                    if lastLogin < timezone.make_aware(datetime.strptime(messages["date"], '%Y-%m-%dT%H:%M:%S.%fZ')):
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
                output.append(currentCollection)
        
        # set accessed time to now
        postgres.ProfileManagement.setLoginTime(user["hashedID"])

        return JsonResponse(output, status=200, safe=False)
    else:
        return HttpResponse("Not logged in", status=401)


