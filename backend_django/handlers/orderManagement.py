"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers managing the orders
"""

import json, random, logging, datetime
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ..services.postgresDB import pgProfiles, pgOrders

from ..handlers.basics import checkIfUserIsLoggedIn, manualCheckifLoggedIn

from ..services import redis, crypto

logger = logging.getLogger(__name__)

#######################################################
@require_http_methods(["GET"])
def createOrderCollectionID(request):
    """
    Create order collection ID for frontend

    :param request: GET Request
    :type request: HTTP GET
    :return: order collection ID as string
    :rtype: JSONResponse

    """
    # generate ID string, make timestamp and create template for order collection
    orderCollectionID = crypto.generateURLFriendlyRandomString()
    now = timezone.now()

    # login defines client
    if manualCheckifLoggedIn(request.session):
        template = {"orderID": orderCollectionID, "client": request.session["pgProfileClass"].getClientID(request.session), "state": 0, "created": str(now), "updated": str(now), "subOrders": {}} 
    else:
        template = {"orderID": orderCollectionID, "client": "", "state": 0, "created": str(now), "updated": str(now), "subOrders": {}} 
    
    # save order collection template in session for now
    if "currentOrder" not in request.session:
        request.session["currentOrder"] = {}
    request.session["currentOrder"][orderCollectionID] = template

    #return just the id for the frontend
    return JsonResponse({"orderID": orderCollectionID})

#######################################################
@require_http_methods(["PATCH"])
def updateOrderCollection(request):
    """
    Update stuff about the order collection

    :param request: Request with content
    :type request: HTTP PATCH
    :return: Message if it worked or not
    :rtype: HTTPResponse

    """
    # TODO: for database orders
    try:
        changes = json.loads(request.body.decode("utf-8"))
        orderCollectionID = changes["orderID"]
        for elem in changes["changes"]:
            request.session["currentOrder"][orderCollectionID][elem] = changes["changes"][elem]
        return HttpResponse("Success")
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed",status=200)


#######################################################
@require_http_methods(["GET"])
def createOrderID(request, orderCollectionID):
    """
    Create order ID for frontend

    :param request: GET Request
    :type request: HTTP GET
    :return: order ID as string
    :rtype: JSONResponse

    """
    # generate ID, timestamp and template for sub order
    orderID = crypto.generateURLFriendlyRandomString()
    now = timezone.now()
    template = {"subOrderID": orderID, "contractor": "", "state": 0, "created": str(now), "updated": str(now), "files": [], "details": {}, "chat": [], "service": {}}
    
    # save into respective order collection
    request.session["currentOrder"][orderCollectionID]["subOrders"][orderID] = template

    # return just the generated ID for frontend
    return JsonResponse({"subOrderID": orderID})

#######################################################
@require_http_methods(["PATCH"])
def updateOrder(request):
    """
    Update stuff about the order

    :param request: Request with content
    :type request: HTTP PATCH
    :return: Message if it worked or not
    :rtype: HTTPResponse

    """
    # TODO: for database orders, sub loops for messages, details, files, ...
    try:
        changes = json.loads(request.body.decode("utf-8"))
        orderCollectionID = changes["orderID"]
        orderID = changes["subOrderID"]
        for elem in changes["changes"]:
            if elem == "service": # service is an array in itself
                for entry in changes["changes"]["service"]:
                    request.session["currentOrder"][orderCollectionID]["subOrders"][orderID]["service"][entry] = changes["changes"]["service"][entry]
            else:
                request.session["currentOrder"][orderCollectionID]["subOrders"][orderID][elem] = changes["changes"][elem]

        return HttpResponse("Success")
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed",status=200)


#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"]) 
def sendOrder(request):
    """
    Save order and send it to manufacturer

    :param request: GET Request
    :type request: HTTP GET
    :return: Response if sent successfully or not
    :rtype: HTTP Response

    """
    # TODO
    try:
        uID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
        selected = request.session["currentOrder"]["cart"]
        if request.session["isPartOfOrganization"]:
            dictForEvents = pgOrders.OrderManagementOrganisation.addOrder(selected, request.session)
        else:
            dictForEvents = pgOrders.OrderManagementUser.addOrder(selected, request.session)
        # Save picture and files in permanent storage


        # send to websockets that are active, that a new message/status is available for that order
        channel_layer = get_channel_layer()
        for userID in dictForEvents:
            values = dictForEvents[userID]
            if userID != pgProfiles.ProfileManagementBase.getUserKey(session=request.session):
                async_to_sync(channel_layer.group_send)(pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=userID), {
                    "type": "sendMessageJSON",
                    "dict": values,
                })
        logger.info(f"{pgProfiles.ProfileManagementBase.getUser(request.session)['name']} ordered something at " + str(datetime.datetime.now()))
        return HttpResponse("Success")
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed")

#######################################################
@require_http_methods(["GET"]) 
def getFlatOrders(request):
    """
    Retrieve orders without much detail.

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with list
    :rtype: JSON Response

    """
    # TODO db
    outDict = {"orders": []}
    for entry in request.session["currentOrder"]:
        tempDict = {}
        tempDict["orderID"] = request.session["currentOrder"][entry]["orderID"]
        tempDict["client"] = request.session["currentOrder"][entry]["client"]
        tempDict["state"] =  request.session["currentOrder"][entry]["state"]
        tempDict["created"] = request.session["currentOrder"][entry]["created"]
        tempDict["updated"] = request.session["currentOrder"][entry]["updated"]
        tempDict["subOrderCount"] = len(request.session["currentOrder"][entry]["subOrders"])
        outDict["orders"].append(tempDict)
    
    return JsonResponse(outDict)

#######################################################
@require_http_methods(["GET"]) 
def getOrder(request, orderCollectionID):
    """
    Retrieve order collection and orders.

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with list
    :rtype: JSON Response

    """
    # TODO db
    outDict = {}
    outDict["orderID"] = request.session["currentOrder"][orderCollectionID]["orderID"]
    outDict["client"] = request.session["currentOrder"][orderCollectionID]["client"]
    outDict["state"] =  request.session["currentOrder"][orderCollectionID]["state"]
    outDict["created"] = request.session["currentOrder"][orderCollectionID]["created"]
    outDict["updated"] = request.session["currentOrder"][orderCollectionID]["updated"]
    outDict["subOrders"] = []
    for elem in request.session["currentOrder"][orderCollectionID]["subOrders"]:
        outDict["subOrders"].append(request.session["currentOrder"][orderCollectionID]["subOrders"][elem])
    
    return JsonResponse(outDict)