"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Basic stuff that is imported everywhere
"""

import datetime
from functools import wraps
from django.http import HttpResponse, JsonResponse

from anyio import sleep

from ..services import rights

#######################################################
def checkIfTokenValid(token):
    """
    Check whether the token of a user has expired and a new login is necessary

    :param token: User session token
    :type token: Dictionary
    :return: True if the token is valid or False if not
    :rtype: Bool
    """
    
    if datetime.datetime.now() > datetime.datetime.strptime(token["tokenExpiresOn"],"%Y-%m-%d %H:%M:%S+00:00"):
        return False
    return True

#################### DECORATOR ###################################
def checkIfUserIsLoggedIn(json=False):
    """
    Check whether a user is logged in or not.

    :param json: Controls if the output is in JSON Format or not
    :type json: Bool
    :return: Response whether the user is logged in or not. If so, call the function.
    :rtype: HTTPRespone/JSONResponse, Func
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if "user" in request.session:
                if checkIfTokenValid(request.session["user"]):
                    return func(request, *args, **kwargs)
                else:
                    if json:
                        return JsonResponse({}, status=401)
                    else:
                        return HttpResponse("Not logged in", status=401)
            else:
                if json:
                    return JsonResponse({}, status=401)
                else:
                    return HttpResponse("Not logged in", status=401)
            
        return inner

    return decorator

#######################################################
def handleTooManyRequestsError(callToAPI):
    """
    Calls the function and checks, if there were too many requests. If so, repeat the request until it's done.
    :param callToAPI: Function call to Auth0 API
    :type callToAPI: Lambda func
    :return: Either an error, or the response
    :rtype: Exception | JSON/Dict
    """
    response = callToAPI()
    iterationVariable = 0
    if response.status_code == 429:
        while response.status_code == 429:
            if iterationVariable > 100:
                return Exception("Too many requests")
            sleep(1)
            response = callToAPI()
            iterationVariable += 1
        return response.json()
    elif response.status_code != 200 and response.status_code != 201 and response.status_code != 202 and response.status_code != 203 and response.status_code != 204:
        return Exception(response.text)
    elif response.status_code == 204:
        return ""
    else:
        return response.json()

#################### DECORATOR ###################################
def checkIfRightsAreSufficient(funcName, json=False):
    """
    Check whether a user has sufficient rights to call that function.

    :param json: Controls if the output is in JSON Format or not
    :type json: Bool
    :return: Response if the rights were not sufficient, function call if they were.
    :rtype: HTTPRespone/JSONResponse, Func
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if "user" in request.session:
                if rights.rightsManagement.checkIfAllowed(request.session["userPermissions"], funcName):
                    return func(request, *args, **kwargs)
                else:
                    if json:
                        return JsonResponse({}, status=403)
                    else:
                        return HttpResponse("Insufficient rights", status=403)
            else:
                if json:
                    return JsonResponse({}, status=403)
                else:
                    return HttpResponse("Insufficient rights", status=403)
            
        return inner

    return decorator    
        
