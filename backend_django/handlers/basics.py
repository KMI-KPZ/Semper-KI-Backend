"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Basic stuff that is imported everywhere
"""

import datetime

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

#######################################################
def checkIfUserIsLoggedIn(request):
    """
    Check whether a user is logged in or not.

    :param request: GET request
    :type request: HTTP GET
    :return: True if the user is logged in or False if not
    :rtype: Bool
    """

    if "user" in request.session:
        if checkIfTokenValid(request.session["user"]):
            return True
        else:
            return False
    else:
        return False
    
#######################################################
def handleTooManyRequestsError(statusCode):
    """
    Checks, ifthere were too many requests
    :param statusCode: Status code of answer
    :type statusCode: Integer
    :return: If so, say so, if not, then don't
    :rtype: Tuple of Bool and String
    """
    if statusCode == 429:
        return (True, "Too many requests! Please wait a bit and try again.")
    else:
        return (False, "")
