"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers using simulation to check the processes
"""

import random, logging
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn
from Generic_Backend.code_General.connections import redis
from Generic_Backend.code_General.definitions import FileObjectContent

from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.handlers.projectAndProcessManagement import getProcessAndProjectFromSession
from code_SemperKI.definitions import ProcessDescription
from code_SemperKI.handlers.files import getFileReadableStream

from ..definitions import ServiceDetails
import requests

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
def getChemnitzData(readableObject, fileName:str = "ein-dateiname.stl") -> dict:
    """
    Send the model to the Chemnitz service and get the dimensions

    :param readableObject: The model to be sent to the service with a .read() method
    :type readableObject: BytesIO | EncryptionAdapter
    :return: data obtained by IWU service
    :rtype: Dict

    """

    result =  {"status_code": 500, "content": {"error": "Fehler"}}

    url = settings.IWS_ENDPOINT + "/properties"
    headers = {'Content-Type': 'model/stl','content-disposition' : f'filename="{fileName}"'}

    try:
        response = requests.post(url, data=readableObject, headers=headers, stream=True)
    except Exception as e:
        logger.warning(f"Error while sending model to Chemnitz service: {str(e)}")
        return {"status_code" : 500, "content": {"error": "Fehler"}}

    # Check the response
    if response.status_code == 200:
        logger.info(f"Success capturing measurements from Chemnitz service")
        result = response.json()
        result["status_code"] = 200

    return result

#######################################################
@require_http_methods(["GET"])
def checkModel(request, processID) -> JsonResponse:
    """
    Ask IWU service for model dimensions

    :param request: GET Request with processID
    :type request: GET
    :return: JSON with dimensions
    :rtype: Json Response

    """
    try:
        project, process = getProcessAndProjectFromSession(request.session, processID)
        if process == None:
            processObj = pgProcesses.ProcessManagementBase.getProcessObj(processID)
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
                "volume": "n.a.",
                "surfaceArea": "n.a.",
                "mbbDimensions": {
                    "_1": "n.a.",
                    "_2": "n.a.",
                    "_3": "n.a.",
                },
                "mbbVolume": "n.a.",
            },
            "status_code": 200
        }

        if settings.IWS_ENDPOINT is None:
            return JsonResponse(mock)

        fileContent, Flag = getFileReadableStream(request, processID, model[FileObjectContent.id])
        if Flag:
            resultData = getChemnitzData(fileContent, modelName)
        else:
            logger.warning(f"Error while accessing file {modelName}")

        if resultData["status_code"] != 200:
            return JsonResponse(mock)
        return JsonResponse(resultData)

    except (Exception) as error:
        logger.error(f'Generic error in checkModel: {str(error)}')
        return JsonResponse({}, status=500)