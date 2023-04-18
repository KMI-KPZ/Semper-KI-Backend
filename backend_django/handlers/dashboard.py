"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers for the dashboard
"""

import json, random
from django.conf import settings
from django.http import HttpResponse, JsonResponse

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
        uID = postgres.ProfileManagement.getUserID(request.session)
        return JsonResponse(postgres.OrderManagement.getOrders(uID), safe=False)
    else:
        return HttpResponse("Not logged in", status=401)
    
#######################################################
def updateOrders(request):
    """
    Update saved orders for dashboard.

    :param request: POST Request
    :type request: HTTP POST
    :return: HTTP Response if update worked
    :rtype: HTTP Response

    """
    if checkIfUserIsLoggedIn(request):
        if request.method == "PUT":
            # TODO retrieve cart
            # TODO change stuff
            pass

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