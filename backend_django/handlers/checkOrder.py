"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers using simulation to check the orders
"""

import json, random, logging, datetime
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ..services.postgresDB import pgProfiles, pgOrders

from ..handlers.basics import checkIfUserIsLoggedIn

from ..services import redis, mocks, crypto

logger = logging.getLogger(__name__)
#######################################################
@require_http_methods(["POST"])
def updateCart(request):
    """
    Save selection of user into session

    :param request: json containing selection
    :type request: JSON
    :return: Response if saving worked or not
    :rtype: HTTP Response

    """
    try:
        selected = json.loads(request.body.decode("utf-8"))
        request.session["selected"] = selected
        return HttpResponse("Success")
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed",status=200)

#######################################################
@require_http_methods(["GET"])
def getCart(request):
    """
    Retrieve selection from session

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON cart
    :rtype: JSON Response

    """
    if "selected" in request.session:
        return JsonResponse(request.session["selected"])
    else:
        return JsonResponse({})

##############################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
def getManufacturers(request):
    """
    Get all suitable manufacturers.

    :param request: GET request
    :type request: HTTP GET
    :return: List of manufacturers and some details
    :rtype: JSON

    """

    manufacturerList = []
    listOfAllManufacturers = pgProfiles.ProfileManagementOrganisation.getAllManufacturers()
    # TODO Check suitability

    # remove unnecessary information and add identifier
    for idx, elem in enumerate(listOfAllManufacturers):
        manufacturerList.append({})
        manufacturerList[idx]["name"] = elem["name"]
        manufacturerList[idx]["id"] = elem["hashedID"]

    return JsonResponse(manufacturerList, safe=False)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
def checkPrintability(request):
    """
    Check if model is printable

    :param request: ?
    :type request: ?
    :return: ?
    :rtype: ?

    """

    model = None
    selected = request.session["selected"]

    (contentOrError, Flag) = redis.retrieveContent(request.session.session_key)
    if Flag:
        # if a model has been uploaded, use that
        model = contentOrError
    else:
        # if not, get selected model
        model = selected["cart"][0]["model"]
    
    material = selected["cart"][0]["material"]
    postProcessing = selected["cart"][0]["postProcessings"]
    # TODO: use simulation service

    # return success or failure
    # outputDict = {}
    # outputDict = {"printability": True}
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(postgres.ProfileManagement.getUserKeyWOSC(session=request.session), {
    #     "type": "sendMessageJSON",
    #     "dict": outputDict,
    # })
    return HttpResponse("Printable")


#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
def checkPrice(request):
    """
    Check how much that'll cost

    :param request: GET Request with json attached
    :type request: Json?
    :return: JSON with prices for various stuff
    :rtype: Json Response

    """
    model = None
    selected = request.session["selected"]

    (contentOrError, Flag) = redis.retrieveContent(request.session.session_key)
    if Flag:
        # if a model has been uploaded, use that
        model = contentOrError
    else:
        # if not, get selected model
        model = selected["cart"][0]["model"]
    
    material = selected["cart"][0]["material"]
    postProcessing = selected["cart"][0]["postProcessings"]

    # TODO: use calculation service

    # THIS IS A MOCK
    summedUpPrices= 0
    for idx, elem in enumerate(selected["cart"]):
        prices = random.randint(1,100) #mocks.mockPrices(elem)
        summedUpPrices += prices
        request.session["selected"]["cart"][idx]["prices"] = prices

    return HttpResponse(summedUpPrices)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
def checkLogistics(request):
    """
    Check how much time stuff'll need

    :param request: GET Request with json attached
    :type request: Json?
    :return: JSON with times for various stuff
    :rtype: Json Response

    """
    model = None
    selected = request.session["selected"]

    (contentOrError, Flag) = redis.retrieveContent(request.session.session_key)
    if Flag:
        # if a model has been uploaded, use that
        model = contentOrError
    else:
        # if not, get selected model
        model = selected["cart"][0]["model"]
    
    material = selected["cart"][0]["material"]
    postProcessing = selected["cart"][0]["postProcessings"]

    # TODO: use calculation service
    summedUpLogistics = 0
    for idx, elem in enumerate(selected["cart"]):
        logistics = random.randint(1,100) #mocks.mockLogistics(elem)
        summedUpLogistics += logistics
        request.session["selected"]["cart"][idx]["logistics"] = logistics
    return HttpResponse(summedUpLogistics)


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

    try:
        uID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
        selected = request.session["selected"]["cart"]
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
