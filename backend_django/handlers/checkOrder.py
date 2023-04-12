"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers using simulation to check the orders
"""

import json, random
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from ..handlers.authentification import checkIfUserIsLoggedIn

from ..services import redis, mocks, postgres, crypto

#######################################################
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
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed",status=200)
    
    return HttpResponse("Success",status=200)

#######################################################
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
def getManufacturers(request):
    """
    Get all suitable manufacturers.

    :param request: GET request
    :type request: HTTP GET
    :return: List of manufacturers and some details
    :rtype: JSON

    """
    manufacturerList = {}
    listOfAllManufacturers = postgres.ProfileManagement.getAllUsersByType("contractor")
    # TODO Check suitability

    # remove unnecessary information and add identifier
    for idx, elem in enumerate(listOfAllManufacturers):
        nameOfManufacturer = elem["name"]
        manufacturerList[idx] = {}
        manufacturerList[idx]["name"] = nameOfManufacturer
        manufacturerList[idx]["id"] = crypto.generateSecureID(nameOfManufacturer)

    return JsonResponse(manufacturerList)

##############################################
def selectManufacturer(request):
    """
    Select a suitable manufacturer and save to session.

    :param request: GET request
    :type request: HTTP GET
    :return: Response if successful
    :rtype: HTTP Response

    """
    request.session["selectedManufacturer"] = request.headers["Manufacturer"]
    return HttpResponse("Success")

#######################################################
def checkPrintability(request):
    """
    Check if model is printable

    :param request: ?
    :type request: ?
    :return: ?
    :rtype: ?

    """
    if checkIfUserIsLoggedIn(request):
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
        return HttpResponse("Printable")
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def checkPrice(request):
    """
    Check how much that'll cost

    :param request: GET Request with json attached
    :type request: Json?
    :return: JSON with prices for various stuff
    :rtype: Json Response

    """
    if checkIfUserIsLoggedIn(request):
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

        summedUpPrices= 0
        for idx, elem in enumerate(selected["cart"]):
            prices = mocks.mockPrices(elem)
            summedUpPrices += prices
            request.session["selected"]["cart"][idx]["prices"] = prices
        return HttpResponse(summedUpPrices)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def checkLogistics(request):
    """
    Check how much time stuff'll need

    :param request: GET Request with json attached
    :type request: Json?
    :return: JSON with times for various stuff
    :rtype: Json Response

    """
    if checkIfUserIsLoggedIn(request):
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
            logistics = mocks.mockLogistics(elem)
            summedUpLogistics += logistics
            request.session["selected"]["cart"][idx]["logistics"] = logistics
        return HttpResponse(summedUpLogistics)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def sendOrder(request):
    """
    Save order and send it to manufacturer

    :param request: GET Request
    :type request: HTTP GET
    :return: Response if sent successfully or not
    :rtype: HTTP Response

    """
    if checkIfUserIsLoggedIn(request):
        try:
            selected = request.session["selected"]
            uID = postgres.ProfileManagement.getUserID(request.session)
            orderID = crypto.generateMD5(str(selected) + crypto.generateSalt())
            postgres.OrderManagement.addOrder(uID,orderID,selected)
            # TODO: send somewhere
            return HttpResponse("Success")
        except (Exception) as error:
            print(error)
            return HttpResponse("Failed")
    else:
        return HttpResponse("Not logged in", status=401)