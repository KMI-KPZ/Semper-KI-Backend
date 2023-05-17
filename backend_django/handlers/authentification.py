"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Authentification handling using Auth0
"""

import json, datetime
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from ..services import auth0, redis, postgres

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
def isLoggedIn(request):
    """
    Check whether the token of a user has expired and a new login is necessary

    :param request: User session token
    :type request: Dictionary
    :return: True if the token is valid or False if not
    :rtype: Bool
    """
    # Initialize session if not done already to generate session key
    if "initialized" not in request.session:
        request.session["initialized"] = True

    # Check if user is already logged in
    if "user" in request.session:
        if checkIfTokenValid(request.session["user"]):
            return HttpResponse("Success",status=200)
        else:
            return HttpResponse("Failed",status=200)
    
    return HttpResponse("Failed",status=200)

#######################################################
def loginUser(request):
    """
    Return a link for redirection to Auth0.

    :param request: GET request
    :type request: HTTP GET
    :return: HTTP Response.
    :rtype: HTTP Link as str

    """
    # set type of user
    if "Usertype" not in request.headers:
        request.session["usertype"] = "user"
    else:
        userType = request.headers["Usertype"]
        if userType == "contractor" or userType == "manufacturer":
            request.session["usertype"] = userType
            request.session["organizationType"] = "manufacturer"
        elif userType == "stakeholder":
            request.session["usertype"] = userType
            request.session["organizationType"] = "stakeholder"
        else:
            request.session["usertype"] = userType


    # set redirect url
    if settings.PRODUCTION:
        forward_url = 'https://dev.semper-ki.org'
    else:
        forward_url = 'http://127.0.0.1:3000'
    
    if "Path" not in request.headers:
        request.session["pathAfterLogin"] = forward_url
    else:
        request.session["pathAfterLogin"] = forward_url + request.headers["Path"]
        
    register = ""
    if "Register" in request.headers:
        if request.headers["Register"] == "true":
            register = "&screen_hint=signup"


    uri = auth0.authorizeRedirect(request, reverse("callbackLogin"))
    # return uri and redirect to register if desired
    return HttpResponse(uri.url + register)

#######################################################
def callbackLogin(request):
    """
    Get information back from Auth0.
    Add user to database if entry doesn't exist.

    :param request: POST request
    :type request: HTTP POST
    :return: URL forwarding with success to frontend/user
    :rtype: HTTP Link as redirect

    """
    # authorize callback token
    token = auth0.authorizeToken(request)

    # convert expiration time to the corresponding date and time
    now = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=token["expires_at"])
    request.session["user"] = token
    request.session["user"]["tokenExpiresOn"] = str(now)

    # check if person is admin
    if "https://auth.semper-ki.org/claims/roles" in request.session["user"]["userinfo"]:
        if len(request.session["user"]["userinfo"]["https://auth.semper-ki.org/claims/roles"]) != 0:
            if request.session["user"]["userinfo"]["https://auth.semper-ki.org/claims/roles"][0] == "semper-admin":
                request.session["usertype"] = "admin"
    
    # Get Data from Database or create entry in it for logged in User
    postgres.ProfileManagement.addUser(request.session)
        
    return HttpResponseRedirect(request.session["pathAfterLogin"])

#######################################################
def getAuthInformation(request):
    """
    Return details about user after login. 
    Accesses the database and creates or gets user.

    :param request: GET request
    :type request: HTTP GET
    :return: User details
    :rtype: Json

    """

    if checkIfUserIsLoggedIn(request):
        # Read user details from Database
        return JsonResponse(postgres.ProfileManagement.getUser(request.session))
    else:
        return JsonResponse({}, status=401)

#######################################################
def logoutUser(request):
    """
    Delete session for this user and log out.

    :param request: GET request
    :type request: HTTP GET
    :return: URL to be forwarded
    :rtype: HTTP URL

    """
    # Delete saved files from redis
    redis.deleteKey(request.session.session_key)

    request.session.clear()
    request.session.flush()

    # return redirect(
    #     f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
    #     + urlencode(
    #         {
    #             #"returnTo": request.build_absolute_uri(reverse("index")),
    #             "returnTo": request.build_absolute_uri('http://localhost:3000/callback/logout'),
    #             "client_id": settings.AUTH0_CLIENT_ID,
    #         },
    #         quote_via=quote_plus,
    #     ),
    # )
    if settings.PRODUCTION:
        callbackString = request.build_absolute_uri('https://dev.semper-ki.org')
    else:
        callbackString = request.build_absolute_uri('http://127.0.0.1:3000')

    return HttpResponse(f"https://{settings.AUTH0_DOMAIN}/v2/logout?" + urlencode({"returnTo": request.build_absolute_uri(callbackString),"client_id": settings.AUTH0_CLIENT_ID,},quote_via=quote_plus,))
