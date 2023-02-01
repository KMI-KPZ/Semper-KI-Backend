import json, datetime
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .profiles import addUser, getUser

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

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
        return True
    else:
        return False

#######################################################
def checkIfTokenExpired(token):
    """
    Check whether the token of a user has expired and a new login is necessary

    :param request: User session token
    :type request: Dictionary
    :return: True if the token is valid or False if not
    :rtype: Bool
    """
    test = datetime.datetime.strptime(token["tokenExpiresOn"],"%Y-%m-%d %H:%M:%S+00:00")
    if datetime.datetime.now() > datetime.datetime.strptime(token["tokenExpiresOn"],"%Y-%m-%d %H:%M:%S+00:00"):
        return False
    return True

#######################################################
def isLoggedIn(request):
    """
    Check whether the token of a user has expired and a new login is necessary

    :param request: User session token
    :type request: Dictionary
    :return: True if the token is valid or False if not
    :rtype: Bool
    """

    if "user" in request.session:
        if checkIfTokenExpired(request.session["user"]):
            return HttpResponse("Successful",status=200)
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
    uri = oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callbackLogin"))
    )
    # return uri
    return HttpResponse(uri.url)

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
    token = oauth.auth0.authorize_access_token(request)
    # convert expiration time to the corresponding date and time
    now = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=token["expires_at"])
    request.session["user"] = token
    request.session["user"]["tokenExpiresOn"] = str(now)
    
    # Get Data from Database or create entry in it for logged in User
    addUser(request)

    # token = json.dumps(token)
    #uri = request.build_absolute_uri(reverse("index"))
    if settings.PRODUCTION:
        forward_url = request.build_absolute_uri('https://dev.semper-ki.org')
    else:
        forward_url = request.build_absolute_uri('http://127.0.0.1:3000')
        
    response = HttpResponseRedirect(forward_url)
    #response["user"] = token # This doesnt work
    # response.set_cookie("authToken", value=token)
    return response
    #return redirect(forward_url, data=token)
    # return redirect(request.build_absolute_uri(reverse("index")))

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
    # TODO check if cookies are expired
    if checkIfUserIsLoggedIn(request):
        # Read user details from Database
        return JsonResponse(getUser(request))
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
        
    response = HttpResponse(f"https://{settings.AUTH0_DOMAIN}/v2/logout?" + urlencode({"returnTo": request.build_absolute_uri(callbackString),"client_id": settings.AUTH0_CLIENT_ID,},quote_via=quote_plus,))
    return response
