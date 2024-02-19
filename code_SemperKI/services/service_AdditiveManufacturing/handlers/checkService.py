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
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn
from Generic_Backend.code_General.connections import redis
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import FileObjectContent

from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.handlers.projectAndProcessManagement import getProcessAndProjectFromSession
from code_SemperKI.definitions import ProcessDescription

from ..utilities import mocks
from ..definitions import ServiceDetails

logger = logging.getLogger("errors")


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

#######################################################
@require_http_methods(["GET"])
def checkModel(request, processID):
    """
    Ask IWU service for model dimensions

    :param request: GET Request with processID
    :type request: GET
    :return: JSON with dimensions
    :rtype: Json Response

    """
    try:
        model = {}
        project, process = getProcessAndProjectFromSession(request.session, processID)
        if process == None:
            processObj = pgProcesses.ProcessManagementBase.getProcessObj("", processID)
            if processObj == None:
                raise Exception("Process not found!")
            
            if ServiceDetails.model not in processObj.serviceDetails:
                raise Exception("Model not found!")
            
            model = processObj.serviceDetails[ServiceDetails.model]
        else:
            if ServiceDetails.model not in process[ProcessDescription.serviceDetails]:
                raise Exception("Model not found!")
            model = process[ProcessDescription.serviceDetails][ServiceDetails.model]
        
        modelName = model[FileObjectContent.fileName]

        mock = {
            "filename": modelName,
            "measurements": {
                "volume": 1.0,
                "surfaceArea": 1.0,
                "mbbDimensions": {
                    "_1": 1.0,
                    "_2": 1.0,
                    "_3": 1.0
                },
                "mbbVolume": 1.0
            }
        }

        return JsonResponse(mock)

    except (Exception) as error:
        logger.error(f'Generic error in checkModel: {str(error)}')
        return JsonResponse({}, status=500)
    