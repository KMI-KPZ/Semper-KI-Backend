"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Authentification handling using Auth0
"""

import json, datetime, requests, logging
from anyio import sleep
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from ..handlers import basics
from django.views.decorators.http import require_http_methods

from ..services import auth0, redis, postgres
    

logger = logging.getLogger(__name__)
#######################################################
@require_http_methods(["GET"])
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
        if basics.checkIfTokenValid(request.session["user"]):
            return HttpResponse("Success",status=200)
        else:
            return HttpResponse("Failed",status=200)
    
    return HttpResponse("Failed",status=200)

#######################################################
@require_http_methods(["GET"])
@basics.checkIfUserIsLoggedIn(json=True)
def provideRightsFile(request):
    """
    Returns the json file containing the rights for the frontend

    :param request: GET request
    :type request: HTTP GET
    :return: JSON Response.
    :rtype: JSONResponse

    """
    with open(str(settings.BASE_DIR) + "/backend_django/rights.json") as rightsFile:
        rightsFileJSON = json.load(rightsFile)
        for elem in rightsFileJSON["Rights"]:
            elem.pop("paths")
        return JsonResponse(rightsFileJSON, safe=False)

            

#######################################################
@require_http_methods(["GET"])
def loginUser(request):
    """
    Return a link for redirection to Auth0.

    :param request: GET request
    :type request: HTTP GET
    :return: HTTP Response.
    :rtype: HTTP Link as str

    """
    # check number of login attempts
    if "numOfLoginAttempts" in request.session:
        if (datetime.datetime.now() - datetime.datetime.strptime(request.session["lastLoginAttempt"],"%Y-%m-%d %H:%M:%S.%f")).seconds > 300:
            request.session["numOfLoginAttempts"] = 0
            request.session["lastLoginAttempt"] = str(datetime.datetime.now())
        else:
            request.session["lastLoginAttempt"] = str(datetime.datetime.now())

        if request.session["numOfLoginAttempts"] > 10:
            return HttpResponse("Too many login attempts! Please wait 5 Minutes.", status=429)
        else:
            request.session["numOfLoginAttempts"] += 1
    else:
        request.session["numOfLoginAttempts"] = 1
        request.session["lastLoginAttempt"] = str(datetime.datetime.now())

    # set type of user
    isPartOfOrganization = False
    if "Usertype" not in request.headers:
        request.session["usertype"] = "user"
    else:
        userType = request.headers["Usertype"]
        if userType == "contractor" or userType == "manufacturer":
            request.session["usertype"] = userType
            request.session["organizationType"] = "manufacturer"
            isPartOfOrganization = True
        elif userType == "stakeholder":
            request.session["usertype"] = userType
            request.session["organizationType"] = "stakeholder"
            isPartOfOrganization = True
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

    if isPartOfOrganization:
        uri = auth0.authorizeRedirectOrga(request, reverse("callbackLogin"))
    else:
        uri = auth0.authorizeRedirect(request, reverse("callbackLogin"))
    # return uri and redirect to register if desired
    return HttpResponse(uri.url + register)

#######################################################
def setOrganizationName(request):
    """
    Set's the Organization name based on the information of the token

    :param request: request containing OAuth Token
    :type request: Dict
    :return: Nothing
    :rtype: None

    """
    if "https://auth.semper-ki.org/claims/organization" in request.session["user"]["userinfo"]:
        if len(request.session["user"]["userinfo"]["https://auth.semper-ki.org/claims/organization"]) != 0:
            request.session["organizationName"] = request.session["user"]["userinfo"]["https://auth.semper-ki.org/claims/organization"].capitalize()
        else:
            request.session["organizationName"] = ""
    else:
        request.session["organizationName"] = ""

#######################################################
def retrieveRolesAndPermissionsForMemberOfOrganization(session):
    """
    Get the roles and the permissions via API from Auth0

    :param session: The session of the user
    :type session: Dict
    :return: Dict with roles and permissions
    :rtype: Dict
    """
    try:
        auth0.apiToken.checkIfExpired()
        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            'Cache-Control': "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = session["user"]["userinfo"]["org_id"]
        userID = postgres.ProfileManagement.getUserKey(session)

        
        response = basics.handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/organizations/{orgID}/members/{userID}/roles', headers=headers) )
        if isinstance(response, Exception):
            raise response
        roles = response
        
        for entry in roles:
            response = basics.handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/roles/{entry["id"]}/permissions', headers=headers) )
            if isinstance(response, Exception):
                raise response
            else:
                permissions = response
        
        outDict = {"roles": roles, "permissions": permissions}
        return outDict
    except Exception as e:
        return e

#######################################################
def setRoleAndPermissionsOfUser(request):
    """
    Set's the role and the permissions of the user based on the information of the token

    :param request: request containing OAuth Token
    :type request: Dict
    :return: Exception or True
    :rtype: Exception or Bool

    """
    try:
        # check if person is admin, global role so check works differently
        if "https://auth.semper-ki.org/claims/roles" in request.session["user"]["userinfo"]:
            if len(request.session["user"]["userinfo"]["https://auth.semper-ki.org/claims/roles"]) != 0:
                if "semper-admin" in request.session["user"]["userinfo"]["https://auth.semper-ki.org/claims/roles"]:
                    request.session["usertype"] = "admin"
                    request.session["userRoles"] = ["semper-admin"]
        
        # now gather roles from organization if the user is in one
        if "org_id" in request.session["user"]["userinfo"]:
            resultDict = retrieveRolesAndPermissionsForMemberOfOrganization(request.session)
            if isinstance(resultDict, Exception):
                raise resultDict
            else:
                request.session["userRoles"] = resultDict["roles"]
                request.session["userPermissions"] = resultDict["permissions"]
        return True
    except Exception as e:
        print(f'Generic Exception: {e}')
        return e

#######################################################
@require_http_methods(["POST", "GET"])
def callbackLogin(request):
    """
    Get information back from Auth0.
    Add user to database if entry doesn't exist.

    :param request: POST request
    :type request: HTTP POST
    :return: URL forwarding with success to frontend/user
    :rtype: HTTP Link as redirect

    """
    try:
        # authorize callback token
        if "organizationType" in request.session:
            token = auth0.authorizeTokenOrga(request)
        else:
            token = auth0.authorizeToken(request)

        # convert expiration time to the corresponding date and time
        now = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=token["expires_at"])
        request.session["user"] = token
        request.session["user"]["tokenExpiresOn"] = str(now)

        # get roles and permissions
        setOrganizationName(request)
        retVal = setRoleAndPermissionsOfUser(request)
        if isinstance(retVal, Exception):
            raise retVal

        # Get Data from Database or create entry in it for logged in User
        postgres.ProfileManagement.addUser(request.session)
            
        logger.info(f"{postgres.ProfileManagement.getUser(request.session)['name']} logged in at " + str(datetime.datetime.now()))
        return HttpResponseRedirect(request.session["pathAfterLogin"])
    except Exception as e:
        returnObj = HttpResponseRedirect(request.session["pathAfterLogin"])
        returnObj.write(str(e))
        return returnObj
    
#######################################################
@basics.checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
def getAuthInformation(request):
    """
    Return details about user after login. 
    Accesses the database and creates or gets user.

    :param request: GET request
    :type request: HTTP GET
    :return: User details
    :rtype: Json

    """
    # Read user details from Database
    return JsonResponse(postgres.ProfileManagement.getUser(request.session))

#######################################################
@basics.checkIfUserIsLoggedIn(json=True)
@require_http_methods("GET")
def getRolesOfUser(request):
    """
    Get Roles of User.

    :param request: GET request
    :type request: HTTP GET
    :return: List of roles
    :rtype: JSONResponse
    """

    if "https://auth.semper-ki.org/claims/roles" in request.session["user"]["userinfo"]:
        if len(request.session["user"]["userinfo"]["https://auth.semper-ki.org/claims/roles"]) != 0:
            return JsonResponse(request.session["user"]["userinfo"]["https://auth.semper-ki.org/claims/roles"], safe=False)
        else:
            return JsonResponse([], safe=False, status=200)
    else:
        return JsonResponse([], safe=False, status=400)

#######################################################
@basics.checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
def getPermissionsOfUser(request):
    """
    Get Permissions of User.

    :param request: GET request
    :type request: HTTP GET
    :return: List of roles
    :rtype: JSONResponse
    """
    if "userPermissions" in request.session:
        if len(request.session["userPermissions"]) != 0:
            outArray = []
            for entry in request.session["userPermissions"]:
                context, permission = entry["permission_name"].split(":")
                outArray.append({"context": context, "permission": permission})

            return JsonResponse(outArray, safe=False)
        else:
            return JsonResponse([], safe=False, status=200)
    else:
        return JsonResponse([], safe=False, status=400)

#######################################################
@basics.checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
def getNewRoleAndPermissionsForUser(request):
    """
    In case the role changed, get new role and new permissions from auth0

    :param request: GET request
    :type request: HTTP GET
    :return: New Permissions for User
    :rtype: JSONResponse
    """
    retVal = setRoleAndPermissionsOfUser(request)
    if isinstance(retVal, Exception):
        return HttpResponse(retVal, status=500)
    return getPermissionsOfUser(request)    

#######################################################
@require_http_methods(["GET"])
def logoutUser(request):
    """
    Delete session for this user and log out.

    :param request: GET request
    :type request: HTTP GET
    :return: URL to be forwarded
    :rtype: HTTP URL

    """
    logger.info(f"{postgres.ProfileManagement.getUser(request.session)['name']} logged out at " + str(datetime.datetime.now()))

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
