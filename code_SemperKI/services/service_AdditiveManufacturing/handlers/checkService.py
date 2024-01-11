"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers using simulation to check the processes
"""

import json, random, logging, datetime
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from Generic_Backend.code_General.utilities import crypto
from ..utilities import mocks

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from code_SemperKI.connections.postgresql import pgProcesses

from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn

from Generic_Backend.code_General.connections import redis

logger = logging.getLogger("logToFile")


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

    (contentOrError, Flag) = redis.RedisConnection().retrieveContent(request.session.session_key)
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

    (contentOrError, Flag) = redis.RedisConnection().retrieveContent(request.session.session_key)
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

    (contentOrError, Flag) = redis.RedisConnection().retrieveContent(request.session.session_key)
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

