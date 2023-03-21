import json, random
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from ..services import redis

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
    
    return HttpResponse("Successful",status=200)

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

#######################################################
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
        model = selected["model"]
    
    material = selected["material"]
    postProcessing = selected["postProcessing"]
    # TODO: use simulation service

    # return success or failure
    return HttpResponse("Printable")