"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling of admin requests for organizations, api calls to auth0
"""

import datetime
import json, requests, logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ..connections.postgresql import pgProfiles
from ..connections import auth0
from ..utilities.basics import checkIfUserIsLoggedIn, handleTooManyRequestsError, checkIfRightsAreSufficient, Logging
from ..definitions import SessionContent

logger = logging.getLogger("logToFile")
#######################################################
def sendEventViaWebsocket(orgID, baseURL, baseHeader, eventName, args):
    """
    Send events to the respective websockets.

    :param orgID: ID of that organization
    :type orgID: str
    :param baseURL: stuff for Auth0
    :type baseURL: str
    :param baseHeader: stuff for Auth0
    :type baseHeader: str
    :param eventName: stuff for frontend
    :type eventName: str
    :param args: other arguments
    :type args: str
    :return: True or exception
    :rtype: Bool or exception
    """
    try:
        channel_layer = get_channel_layer()
        if eventName == "assignRole" or eventName == "removeRole":
            groupName = pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=args)
            async_to_sync(channel_layer.group_send)(groupName, {
                "type": "sendMessageJSON",
                "dict": {"eventType": "permissionEvent", "type": "roleChanged"},
            })

        elif eventName == "addPermissionsToRole" or eventName == "editRole":
            # get list of all members, retrieve the user ids and filter for those affected
            response = handleTooManyRequestsError(lambda : requests.get(f'{baseURL}/api/v2/organizations/{orgID}/members', headers=baseHeader) )
            if isinstance(response, Exception):
                raise response
            responseDict = response
            for user in responseDict:
                userID = user["user_id"]
                
                resp = handleTooManyRequestsError(lambda : requests.get(f'{baseURL}/api/v2/organizations/{orgID}/members/{userID}/roles', headers=baseHeader) )
                if isinstance(resp, Exception):
                    raise resp    
                groupName = pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=userID)
                for elem in resp:
                    if elem["id"] == args:
                        async_to_sync(channel_layer.group_send)(groupName, {
                            "type": "sendMessageJSON",
                            "dict": {"eventType": "permissionEvent", "type": "roleChanged"},
                        })

        elif eventName == "deleteUserFromOrganization":
            async_to_sync(channel_layer.group_send)(pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=args), {
                "type": "sendMessageJSON",
                "dict": {"eventType": "orgaEvent", "type": "userDeleted"},
            })

        return True
    except Exception as e:
        return e


#######################################################
def getOrganizationName(session, orgID, baseURL, baseHeader):
    """
    Get Name of the Organization

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :return: If successful, name of organization, error if not
    :rtype: str or error
    """
    try:
        if SessionContent.ORGANIZATION_NAME in session:
            if session[SessionContent.ORGANIZATION_NAME] != "":
                return session[SessionContent.ORGANIZATION_NAME]
        
        res = handleTooManyRequestsError(lambda : requests.get(f'{baseURL}/api/v2/organizations/{orgID}', headers=baseHeader))
        if isinstance(res, Exception):
            raise res
        return res["display_name"].capitalize()
    except Exception as e:
        return e

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organizations_getInviteLink(request):
    """
    Ask Auth0 API to invite someone via e-mail and retrieve the link

    :param request: Request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse
    """
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return HttpResponse("Mock")
        
        content = json.loads(request.body.decode("utf-8"))["data"]

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]
        userName = request.session["user"]["userinfo"]["nickname"]
        emailAdressOfUserToBeAdded = content["content"]["email"]
        roleID = content["content"]["roleID"]

        data = { "inviter": { "name": userName }, "invitee": { "email": emailAdressOfUserToBeAdded }, "client_id": settings.AUTH0_ORGA_CLIENT_ID, "connection_id": "con_t6i9YJzm5KLo4Jlf", "ttl_sec": 0, "roles": [roleID], "send_invitation_email": False }
        
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations/{orgID}/invitations', headers=headers, json=data))
        if isinstance(response, Exception):
            raise response
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},invite,{Logging.Object.USER},user {emailAdressOfUserToBeAdded} to {orgID}," + str(datetime.datetime.now()))
        return HttpResponse(response["invitation_url"])
    
    except Exception as e:
        logger.error(f'Generic Exception while obtaining invite link: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organizations_addUser(request):
    """
    Ask Auth0 API to invite someone via e-mail

    :param request: Request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse
    """
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return HttpResponse("Mock")

        content = json.loads(request.body.decode("utf-8"))["data"]

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]
        userName = request.session["user"]["userinfo"]["nickname"]
        emailAdressOfUserToBeAdded = content["content"]["email"]
        roleID = content["content"]["roleID"]

        data = { "inviter": { "name": userName }, "invitee": { "email": emailAdressOfUserToBeAdded }, "client_id": settings.AUTH0_ORGA_CLIENT_ID, "connection_id": "con_t6i9YJzm5KLo4Jlf", "ttl_sec": 0, "roles":[roleID], "send_invitation_email": True }
        
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations/{orgID}/invitations', headers=headers, json=data))
        if isinstance(response, Exception):
            raise response
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},invite,{Logging.Object.USER},user {emailAdressOfUserToBeAdded} to {orgID}," + str(datetime.datetime.now()))
        return HttpResponse("Success", status=200)

    except Exception as e:
        logger.error(f'Generic Exception while adding user: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def organizations_fetchUsers(request):
    """
    Ask Auth0 API for all users of an organization

    :param request: Request with session in it
    :type request: HTTP GET
    :return: If successful or not
    :rtype: Json or error
    """
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return JsonResponse({})

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]

        orgaName = getOrganizationName(request.session, orgID, baseURL, headers)
        if isinstance(orgaName, Exception):
            raise orgaName

        response = handleTooManyRequestsError(lambda : requests.get(f'{baseURL}/api/v2/organizations/{orgID}/members', headers=headers) )
        if isinstance(response, Exception):
            raise response
        
        responseDict = response
        for idx, entry in enumerate(responseDict):
            resp = handleTooManyRequestsError(lambda : requests.get(f'{baseURL}/api/v2/organizations/{orgID}/members/{entry["user_id"]}/roles', headers=headers) )
            if isinstance(resp, Exception):
                raise resp
            responseDict[idx]["roles"] = resp
            for elemIdx in range(len(responseDict[idx]["roles"])):
                responseDict[idx]["roles"][elemIdx]["name"] = responseDict[idx]["roles"][elemIdx]["name"].replace(orgaName+"-", "")
            entry.pop("user_id")

        return JsonResponse(responseDict, safe=False)
    except Exception as e:
        logger.error(f'Generic Exception while fetching users: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organizations_deleteUser(request):
    """
    Ask Auth0 API to delete someone from an organization via their name

    :param request: Request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse or error
    """
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return HttpResponse("Mock")

        content = json.loads(request.body.decode("utf-8"))["data"]
        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]
        userName = request.session["user"]["userinfo"]["nickname"]
        emailAdressOfUserToBeAdded = content["content"]["email"]

        # fetch user id via E-Mail of the user
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/users?q=email:"{emailAdressOfUserToBeAdded}"&search_engine=v3', headers=headers) )
        if isinstance(response, Exception):
            raise response
        userID = response[0]["user_id"]

        # delete person from organization via userID
        data = { "members": [userID]}
        response = handleTooManyRequestsError( lambda : requests.delete(f'{baseURL}/api/v2/organizations/{orgID}/members', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response
        pgProfiles.ProfileManagement.deleteUser("", uID=userID)
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.DELETED},deleted,{Logging.Object.USER},user {emailAdressOfUserToBeAdded} from {orgID}," + str(datetime.datetime.now()))
        
        # Send event to websocket
        retVal = sendEventViaWebsocket(orgID, baseURL, headers, "deleteUserFromOrganization", userID)
        if isinstance(retVal, Exception):
            raise retVal
        
        return HttpResponse("Success", status=200)

    except Exception as e:
        logger.error(f'Generic Exception while deleting user: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def organizations_createRole(request):
    """
    Ask Auth0 API to create a new role

    :param request: request with json as content
    :type request: HTTP POST
    :return: If successful or not
    :rtype: JSON or Error
    """
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return JsonResponse({})

        content = json.loads(request.body.decode("utf-8"))["data"]

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]
        userName = request.session["user"]["userinfo"]["nickname"]

        orgaName = getOrganizationName(request.session, orgID, baseURL, headers)
        if isinstance(orgaName, Exception):
            raise orgaName
        
        # append organization name to the role name to avoid that two different organizations create the same role
        roleName = orgaName + "-" + content["content"]["roleName"]
        roleDescription = content["content"]["roleDescription"]

        data = { "name": roleName, "description": roleDescription}
        response = handleTooManyRequestsError( lambda: requests.post(f'{baseURL}/api/v2/roles', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},role {roleName} in {orgID}," + str(datetime.datetime.now()))
        return JsonResponse(response, safe=False)
    
    except Exception as e:
        logger.error(f'Generic Exception while creating role: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organizations_assignRole(request):
    """
    Assign a role to a person

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse
    """
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return HttpResponse("Mock")

        content = json.loads(request.body.decode("utf-8"))["data"]

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]
        userName = request.session["user"]["userinfo"]["nickname"]
        emailAdressOfUserToBeAdded = content["content"]["email"]
        roleID = content["content"]["roleID"]

        # fetch user id via E-Mail of the user
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/users?q=email:"{emailAdressOfUserToBeAdded}"&search_engine=v3', headers=headers) )
        if isinstance(response, Exception):
            raise response
        userID = response[0]["user_id"]

        data = { "roles": [roleID]}
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations/{orgID}/members/{userID}/roles', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response

        retVal = sendEventViaWebsocket(orgID, baseURL, headers, "assignRole", userID)
        if isinstance(retVal, Exception):
            raise retVal
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.DEFINED},assigned,{Logging.Object.OBJECT},role {roleID} to {emailAdressOfUserToBeAdded} in {orgID}," + str(datetime.datetime.now()))
        return HttpResponse("Success", status=200)

    except Exception as e:
        logger.error(f'Generic Exception while assigning role: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organizations_removeRole(request):
    """
    Remove a role from a person

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: True or error
    """
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return HttpResponse("Mock")

        content = json.loads(request.body.decode("utf-8"))["data"]

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]
        userName = request.session["user"]["userinfo"]["nickname"]
        emailAdressOfUserToBeAdded = content["content"]["email"]
        roleID = content["content"]["roleID"]

        # fetch user id via E-Mail of the user
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/users?q=email:"{emailAdressOfUserToBeAdded}"&search_engine=v3', headers=headers) )
        if isinstance(response, Exception):
            raise response
        userID = response[0]["user_id"]

        data = { "roles": [roleID]}
        response = handleTooManyRequestsError( lambda : requests.delete(f'{baseURL}/api/v2/organizations/{orgID}/members/{userID}/roles', headers=headers, json=data))
        if isinstance(response, Exception):
            raise response
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.DELETED},removed,{Logging.Object.OBJECT},role {roleID} from {emailAdressOfUserToBeAdded} in {orgID}," + str(datetime.datetime.now()))
        # retVal = sendEventViaWebsocket(orgID, baseURL, headers, "removeRole", result)
        # if isinstance(retVal, Exception):
        #     raise retVal
        return HttpResponse("Success", status=200)
        
    except Exception as e:
        logger.error(f'Generic Exception while removing role: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organizations_editRole(request):
    """
    Ask Auth0 API to edit a role

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful true or an error if not
    :rtype: Bool or error
    """
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return HttpResponse("Mock")

        content = json.loads(request.body.decode("utf-8"))["data"]

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]
        userName = request.session["user"]["userinfo"]["nickname"]

        orgaName = getOrganizationName(request.session, orgID, baseURL, headers)
        if isinstance(orgaName, Exception):
            raise orgaName

        roleID = content["content"]["roleID"]
        roleName = orgaName + "-" + content["content"]["roleName"]
        roleDescription = content["content"]["roleDescription"]

        data = { "name": roleName, "description": roleDescription}
        response = handleTooManyRequestsError( lambda : requests.patch(f'{baseURL}/api/v2/roles/{roleID}', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response
        
        retVal = sendEventViaWebsocket(orgID, baseURL, headers, "editRole", roleID)
        if isinstance(retVal, Exception):
            raise retVal
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.EDITED},edited,{Logging.Object.OBJECT},role {roleName} for {orgID}," + str(datetime.datetime.now()))
        return HttpResponse("Success", status=200)

    except Exception as e:
        logger.error(f'Generic Exception while editing role: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)


#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def organizations_getRoles(request):
    """
    Fetch all roles for the organization

    :param request: request with session
    :type request: HTTP GET
    :return: If successful, list of roles for that organization, error if not
    :rtype: JSON or error
    """
    try:

        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return JsonResponse({})

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]

        orgaName = getOrganizationName(request.session, orgID, baseURL, headers)
        if isinstance(orgaName, Exception):
            raise orgaName

        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/roles', headers=headers) )
        if isinstance(response, Exception):
            raise response
        roles = response
        rolesOut = []
        for entry in roles:
            if orgaName in entry["name"]:
                entry["name"] = entry["name"].replace(orgaName+"-", "")
                rolesOut.append(entry)

        return JsonResponse(rolesOut, safe=False)
    
    except Exception as e:
        logger.error(f'Generic Exception while fetching roles: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organizations_deleteRole(request):
    """
    Delete role via ID

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse or error
    """
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return HttpResponse("Mock")

        content = json.loads(request.body.decode("utf-8"))["data"]

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        roleID = content["content"]["roleID"]
        userName = request.session["user"]["userinfo"]["nickname"]
        orgID = request.session["user"]["userinfo"]["org_id"]

        response = handleTooManyRequestsError( lambda : requests.delete(f'{baseURL}/api/v2/roles/{roleID}', headers=headers) )
        if isinstance(response, Exception):
            raise response
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},role {roleID} from {orgID}," + str(datetime.datetime.now()))
        return HttpResponse("Success", status=200)
        
    except Exception as e:
        logger.error(f'Generic Exception while deleting role: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organizations_setPermissionsForRole(request):
    """
    Add Permissions to role

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse or error
    """    
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return HttpResponse("Mock")

        content = json.loads(request.body.decode("utf-8"))["data"]

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]
        userName = request.session["user"]["userinfo"]["nickname"]
        roleID = content["content"]["roleID"]
        permissionList = content["content"]["permissionIDs"]

        data = {"permissions" : []}
        for entry in permissionList:
            data["permissions"].append({"resource_server_identifier": "back.semper-ki.org", "permission_name": entry})
        
        # get all permissions, remove them, then add anew. It's cumbersome but the API is the way it is
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/roles/{roleID}/permissions', headers=headers) )
        if isinstance(response, Exception):
            raise response
        permissionsToBeRemoved = {"permissions": []}
        for entry in response:
            permissionsToBeRemoved["permissions"].append({"resource_server_identifier": "back.semper-ki.org", "permission_name": entry["permission_name"]})
        if len(permissionsToBeRemoved["permissions"]) > 0: # there are permissions that need removal
            response = handleTooManyRequestsError( lambda : requests.delete(f'{baseURL}/api/v2/roles/{roleID}/permissions', headers=headers, json=permissionsToBeRemoved) )
            if isinstance(response, Exception):
                raise response
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/roles/{roleID}/permissions', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response
        
        retVal = sendEventViaWebsocket(orgID, baseURL, headers, "addPermissionsToRole", roleID)
        if isinstance(retVal, Exception):
            raise retVal
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.DEFINED},set,{Logging.Object.OBJECT},permissions of role {roleID} in {orgID}," + str(datetime.datetime.now()))
        return HttpResponse("Success", status=200)

    except Exception as e:
        logger.error(f'Generic Exception while setting permissions for role: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def organizations_getPermissions(request):
    """
    Get all Permissions

    :param request: request with session
    :type request: HTTP GET
    :return: If successful, list of permissions for role as array, error if not
    :rtype: JSON or error
    """ 
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return JsonResponse({})

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"

        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/resource-servers/back.semper-ki.org', headers=headers) )
        if isinstance(response, Exception):
            raise response
        
        return JsonResponse(response["scopes"],safe=False)

    except Exception as e:
        logger.error(f'Generic Exception while fetching permissions: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def organizations_getPermissionsForRole(request):
    """
    Get Permissions of role

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful, list of permissions for role as array, error if not
    :rtype: JSON or error
    """    
    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return JsonResponse({})

        content = json.loads(request.body.decode("utf-8"))["data"]

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        roleID = content["content"]["roleID"]

        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/roles/{roleID}/permissions', headers=headers) )
        if isinstance(response, Exception):
            raise response
        return JsonResponse(response,safe=False)

    except Exception as e:
        logger.error(f'Generic Exception while fetching permissions for role: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@require_http_methods(["POST"])
def organizations_createNewOrganization(request):
    """
    Create a new organization, create an admin role, invite a person via email as admin.
    All via Auth0s API.

    :param request: request with content as json
    :type request: HTTP POST
    :return: Successfull or not
    :rtype: HTTPResponse
    """    

    try:
        if SessionContent.MOCKED_LOGIN in request.session and request.session[SessionContent.MOCKED_LOGIN] is True:
            return HttpResponse("Mock")

        content = json.loads(request.body.decode("utf-8"))["data"]

        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"

        # create organization
        metadata = {} if "metadata" not in content["content"] else content["content"]["metadata"]
        data = { "name": content["content"]["name"], 
                "display_name": content["content"]["display_name"], 
                "branding":
                    { "logo_url": content["content"]["logo_url"], 
                     "colors": 
                     { "primary": content["content"]["primary_color"], 
                        "page_background": content["content"]["background_color"] }
                    },
                "metadata": metadata,
                "enabled_connections": [ { "connection_id": "con_t6i9YJzm5KLo4Jlf", "assign_membership_on_login": False } ] }

        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response
        
        org_id = response["id"]
        
        # create admin role
        roleName = content["content"]["display_name"] + "-" + "admin"
        roleDescription = "admin"

        data = { "name": roleName, "description": roleDescription}
        response = handleTooManyRequestsError( lambda: requests.post(f'{baseURL}/api/v2/roles', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response
        roleID = response["id"]

        # connect admin role with permissions
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/resource-servers/back.semper-ki.org', headers=headers) )
        if isinstance(response, Exception):
            raise response

        data = {"permissions": []}
        for entry in response["scopes"]:
            data["permissions"].append({"resource_server_identifier": "back.semper-ki.org", "permission_name": entry["value"]})

        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/roles/{roleID}/permissions', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response

        # invite person to organization as admin
        email = content["content"]["email"]

        data = { "inviter": { "name": "Semper-KI" }, "invitee": { "email": email }, "client_id": settings.AUTH0_ORGA_CLIENT_ID, "roles": [ roleID ], "connection_id": "con_t6i9YJzm5KLo4Jlf", "ttl_sec": 0, "send_invitation_email": True }
        
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations/{org_id}/invitations', headers=headers, json=data))
        if isinstance(response, Exception):
            raise response
        
        logger.info(f"{Logging.Subject.SYSTEM},Semper-KI,{Logging.Predicate.CREATED},created,{Logging.Object.ORGANISATION},{content['content']['name']} through user {email}," + str(datetime.datetime.now()))
        
        return HttpResponse("Success", status=200)
    
    except Exception as e:
        logger.error(f'Generic Exception while creating organization: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)    

