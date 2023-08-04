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

from ..services.postgresDB import pgProfiles

from ..services import auth0
from ..handlers.basics import checkIfUserIsLoggedIn, handleTooManyRequestsError, checkIfRightsAreSufficient

logger = logging.getLogger(__name__)
#######################################################
def sendEventViaWebsocket(orgID, baseURL, baseHeader, eventName, args):
    """
    """
    try:
        channel_layer = get_channel_layer()
        if eventName == "assignRole" or eventName == "removeRole":
            async_to_sync(channel_layer.group_send)(pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=args), {
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
                for elem in resp:
                    if elem["id"] == args:
                        async_to_sync(channel_layer.group_send)(pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=userID), {
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
        if "organizationName" in session:
            if session["organizationName"] != "":
                return session["organizationName"]
        
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
def organisations_getInviteLink(request):
    """
    Ask Auth0 API to invite someone via e-mail and retrieve the link

    :param request: Request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse
    """
    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]
        userName = request.session["user"]["userinfo"]["nickname"]
        emailAdressOfUserToBeAdded = content["content"]["email"]

        data = { "inviter": { "name": userName }, "invitee": { "email": emailAdressOfUserToBeAdded }, "client_id": settings.AUTH0_ORGA_CLIENT_ID, "connection_id": "con_t6i9YJzm5KLo4Jlf", "ttl_sec": 0, "send_invitation_email": False }
        
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations/{orgID}/invitations', headers=headers, json=data))
        if isinstance(response, Exception):
            raise response
        
        logger.info(f"{userName} invited the user {emailAdressOfUserToBeAdded} at " + str(datetime.datetime.now()))
        return HttpResponse(response["invitation_url"])
    
    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organisations_addUser(request):
    """
    Ask Auth0 API to invite someone via e-mail

    :param request: Request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse
    """
    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        orgID = request.session["user"]["userinfo"]["org_id"]
        userName = request.session["user"]["userinfo"]["nickname"]
        emailAdressOfUserToBeAdded = content["content"]["email"]

        data = { "inviter": { "name": userName }, "invitee": { "email": emailAdressOfUserToBeAdded }, "client_id": settings.AUTH0_ORGA_CLIENT_ID, "connection_id": "con_t6i9YJzm5KLo4Jlf", "ttl_sec": 0, "send_invitation_email": True }
        
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations/{orgID}/invitations', headers=headers, json=data))
        if isinstance(response, Exception):
            raise response
        
        logger.info(f"{userName} invited the user {emailAdressOfUserToBeAdded} at " + str(datetime.datetime.now()))
        return HttpResponse("Success", status=200)

    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def organisations_fetchUsers(request):
    """
    Ask Auth0 API for all users of an organisation

    :param request: Request with session in it
    :type request: HTTP GET
    :return: If successful or not
    :rtype: Json or error
    """
    try:

        auth0.apiToken.checkIfExpired()
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
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organisations_deleteUser(request):
    """
    Ask Auth0 API to delete someone from an organization via their name

    :param request: Request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse or error
    """
    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
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
        logger.info(f"{userName} deleted the user {emailAdressOfUserToBeAdded} at " + str(datetime.datetime.now()))
        
        # Send event to websocket
        retVal = sendEventViaWebsocket(orgID, baseURL, headers, "deleteUserFromOrganization", userID)
        if isinstance(retVal, Exception):
            raise retVal
        
        return HttpResponse("Success", status=200)

    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def organisations_createRole(request):
    """
    Ask Auth0 API to create a new role

    :param request: request with json as content
    :type request: HTTP POST
    :return: If successful or not
    :rtype: JSON or Error
    """
    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
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
        
        logger.info(f"{userName} created the role {roleName} at " + str(datetime.datetime.now()))
        return JsonResponse(response, safe=False)
    
    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organisations_assignRole(request):
    """
    Assign a role to a person

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse
    """
    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
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
        
        logger.info(f"{userName} assigned the role {roleID} to {emailAdressOfUserToBeAdded} at " + str(datetime.datetime.now()))
        return HttpResponse("Success", status=200)

    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organisations_removeRole(request):
    """
    Remove a role from a person

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: True or error
    """
    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
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
        
        logger.info(f"{userName} removed the role {roleID} from {emailAdressOfUserToBeAdded} at " + str(datetime.datetime.now()))
        # retVal = sendEventViaWebsocket(orgID, baseURL, headers, "removeRole", result)
        # if isinstance(retVal, Exception):
        #     raise retVal
        return HttpResponse("Success", status=200)
        
    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organisations_editRole(request):
    """
    Ask Auth0 API to edit a role

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful true or an error if not
    :rtype: Bool or error
    """
    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
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
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/roles/{roleID}', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response
        
        retVal = sendEventViaWebsocket(orgID, baseURL, headers, "editRole", roleID)
        if isinstance(retVal, Exception):
            raise retVal
        logger.info(f"{userName} edited the role {roleName} at " + str(datetime.datetime.now()))
        return HttpResponse("Success", status=200)

    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)


#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def organisations_getRoles(request):
    """
    Fetch all roles for the organization

    :param request: request with session
    :type request: HTTP GET
    :return: If successful, list of roles for that organization, error if not
    :rtype: JSON or error
    """
    try:
        auth0.apiToken.checkIfExpired()
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
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organisations_deleteRole(request):
    """
    Delete role via ID

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse or error
    """
    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"
        roleID = content["content"]["roleID"]
        userName = request.session["user"]["userinfo"]["nickname"]

        response = handleTooManyRequestsError( lambda : requests.delete(f'{baseURL}/api/v2/roles/{roleID}', headers=headers) )
        if isinstance(response, Exception):
            raise response
        
        logger.info(f"{userName} deleted the role {roleID} at " + str(datetime.datetime.now()))
        return HttpResponse("Success", status=200)
        
    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
def organisations_setPermissionsForRole(request):
    """
    Add Permissions to role

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful or not
    :rtype: HTTPResponse or error
    """    
    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
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
        response = handleTooManyRequestsError( lambda : requests.delete(f'{baseURL}/api/v2/roles/{roleID}/permissions', headers=headers, json=permissionsToBeRemoved) )
        if isinstance(response, Exception):
            raise response
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/roles/{roleID}/permissions', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response
        
        retVal = sendEventViaWebsocket(orgID, baseURL, headers, "addPermissionsToRole", roleID)
        if isinstance(retVal, Exception):
            raise retVal
        logger.info(f"{userName} set permissions of role {roleID} at " + str(datetime.datetime.now()))
        return HttpResponse("Success", status=200)

    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def organisations_getPermissions(request):
    """
    Get all Permissions

    :param request: request with session
    :type request: HTTP GET
    :return: If successful, list of permissions for role as array, error if not
    :rtype: JSON or error
    """ 
    try:
        auth0.apiToken.checkIfExpired()
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
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def organisations_getPermissionsForRole(request):
    """
    Get Permissions of role

    :param request: request with content as json
    :type request: HTTP POST
    :return: If successful, list of permissions for role as array, error if not
    :rtype: JSON or error
    """    
    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
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
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)

#######################################################
@checkIfUserIsLoggedIn
@require_http_methods(["POST"])
def organisations_createNewOrganisation(request):
    """
    Create a new organisation, create an admin role, invite a person via email as admin.
    All via Auth0s API.

    :param request: request with content as json
    :type request: HTTP POST
    :return: Successfull or not
    :rtype: HTTPResponse
    """    

    try:
        content = json.loads(request.body.decode("utf-8"))["data"]

        auth0.apiToken.checkIfExpired()
        headers = {
            'authorization': f'Bearer {auth0.apiToken.accessToken}',
            'content-Type': 'application/json',
            "Cache-Control": "no-cache"
        }
        baseURL = f"https://{settings.AUTH0_DOMAIN}"

        # create organisation
        data = { "name": content["content"]["name"], 
                "display_name": content["content"]["display_name"], 
                "branding":
                    { "logo_url": content["content"]["logo_url"], 
                     "colors": 
                     { "primary": content["content"]["primary_color"], 
                        "page_background": content["content"]["background_color"] }
                    },
                "metadata": content["content"]["metadata"],
                "enabled_connections": [ { "connection_id": "con_t6i9YJzm5KLo4Jlf", "assign_membership_on_login": False } ] }

        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organisations', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response
        
        org_id = response["id"]
        
        # create admin role
        roleName = content["content"]["name"] + "-" + "admin"
        roleDescription = "admin"

        data = { "name": roleName, "description": roleDescription}
        response = handleTooManyRequestsError( lambda: requests.post(f'{baseURL}/api/v2/roles', headers=headers, json=data) )
        if isinstance(response, Exception):
            raise response
        roleID = response["id"]

        # invite person to organisation as admin
        email = content["content"]["email"]

        data = { "inviter": { "name": "Semper-KI" }, "invitee": { "email": email }, "client_id": settings.AUTH0_ORGA_CLIENT_ID, "roles": [ roleID ], "connection_id": "con_t6i9YJzm5KLo4Jlf", "ttl_sec": 0, "send_invitation_email": True }
        
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations/{org_id}/invitations', headers=headers, json=data))
        if isinstance(response, Exception):
            raise response
        
        logger.info(f"Semper-KI created organisation {content['content']['name']} and invited the user {email} at " + str(datetime.datetime.now()))
        
        return HttpResponse("Success", status=200)
    
    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)    

