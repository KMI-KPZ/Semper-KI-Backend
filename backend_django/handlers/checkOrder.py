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
        model = selected["models"]
    
    material = selected["materials"]
    postProcessing = selected["postProcessing"]
    # TODO: use simulation service

    # return success or failure
    return HttpResponse("Printable")

#######################################################
def mockPrices(selection):
    mockFactors = {"materials": {
                "ABS": 1,
                "PLA": 2,
                "Standard resin": 3,
                "Polyurethane resin": 4,
                "Titanium": 5,
                "Stainless steel": 6
            },
            "postProcessing": {
                "postProcessing1": 1,
                "postProcessing2": 2,
                "postProcessing3": 3
            }
    }

    mockPrices = {
        "material": mockFactors["materials"][selection["materials"]["title"]] * 10,
        "postProcessing": mockFactors["postProcessing"][selection["postProcessing"]["title"]] * 5,
        "logistics": random.randint(1,100)
    }

    mockPrices["totalPrice"] = mockPrices["material"] + mockPrices["postProcessing"]

    return mockPrices

#######################################################
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
        model = selected["model"]
    
    material = selected["materials"]
    postProcessing = selected["postProcessing"]

    # TODO: use calculation service

    return JsonResponse(mockPrices(selected))

#######################################################
def mockLogistics(selection):
    mockFactors = {"materials": {
                "ABS": 1,
                "PLA": 2,
                "Standard resin": 3,
                "Polyurethane resin": 4,
                "Titanium": 5,
                "Stainless steel": 6
            },
            "postProcessing": {
                "postProcessing1": 1,
                "postProcessing2": 2,
                "postProcessing3": 3
            }
    }

    mockTimes = {
        "material": mockFactors["materials"][selection["materials"]["title"]] * 5,
        "postProcessing": mockFactors["postProcessing"][selection["postProcessing"]["title"]] * 1,
        "delivery": random.randint(1,10)
    }

    mockTimes["production"] = mockTimes["material"] + mockTimes["postProcessing"]

    return mockTimes

#######################################################
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
        model = selected["model"]
    
    material = selected["materials"]
    postProcessing = selected["postProcessing"]

    # TODO: use calculation service

    return JsonResponse(mockLogistics(selected))