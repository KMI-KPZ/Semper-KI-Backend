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

from ..services import auth0, postgres
from ..handlers.basics import checkIfUserIsLoggedIn, handleTooManyRequestsError

logger = logging.getLogger(__name__)
#######################################################
def sendEventViaWebsocket(orgID, baseURL, baseHeader, eventName, args):
    """
    """
    try:
        channel_layer = get_channel_layer()
        if eventName == "assignRole" or eventName == "removeRole":
            async_to_sync(channel_layer.group_send)(postgres.ProfileManagement.getUserKeyWOSC(uID=args), {
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
                        async_to_sync(channel_layer.group_send)(postgres.ProfileManagement.getUserKeyWOSC(uID=userID), {
                            "type": "sendMessageJSON",
                            "dict": {"eventType": "permissionEvent", "type": "roleChanged"},
                        })

        elif eventName == "deleteUserFromOrganization":
            async_to_sync(channel_layer.group_send)(postgres.ProfileManagement.getUserKeyWOSC(uID=args), {
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
def sendInvite(orgID, baseURL, baseHeader, nameOfCurrentUser, withEmail, emailAdressOfUserToBeAdded):
    """
    Ask Auth0 API to invite someone via e-mail

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param nameOfCurrentUser: Name of the user that adds people
    :type nameOfCurrentUser: str
    :param emailAdressOfUserToBeAdded: E-Mail adress of the user that shall be added
    :type emailAdressOfUserToBeAdded: str
    :return: If successful or not
    :rtype: Bool, json or error
    """
    try:
        header = baseHeader
        header["Cache-Control"] = "no-cache"

        data = { "inviter": { "name": nameOfCurrentUser }, "invitee": { "email": emailAdressOfUserToBeAdded }, "client_id": settings.AUTH0_ORGA_CLIENT_ID, "connection_id": "con_t6i9YJzm5KLo4Jlf", "ttl_sec": 0, "send_invitation_email": True }
        if withEmail:

            response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations/{orgID}/invitations', headers=header, json=data))
            if isinstance(response, Exception):
                raise response
            return True
        else:
            data["send_invitation_email"] = False

            response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations/{orgID}/invitations', headers=header, json=data))
            if isinstance(response, Exception):
                raise response
            return response
    except Exception as e:
        return e

#######################################################
def getMembersOfOrganization(orgID, baseURL, baseHeader, orgaName):
    """
    Ask Auth0 API to invite someone via e-mail

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param orgaName: Name of organization
    :type orgaName: str
    :return: If successful or not
    :rtype: Json or error
    """
    try:
        response = handleTooManyRequestsError(lambda : requests.get(f'{baseURL}/api/v2/organizations/{orgID}/members', headers=baseHeader) )
        if isinstance(response, Exception):
            raise response
        responseDict = response
        for idx, entry in enumerate(responseDict):
            resp = handleTooManyRequestsError(lambda : requests.get(f'{baseURL}/api/v2/organizations/{orgID}/members/{entry["user_id"]}/roles', headers=baseHeader) )
            if isinstance(resp, Exception):
                raise resp
            responseDict[idx]["roles"] = resp
            for elemIdx in range(len(responseDict[idx]["roles"])):
                responseDict[idx]["roles"][elemIdx]["name"] = responseDict[idx]["roles"][elemIdx]["name"].replace(orgaName+"-", "")
            entry.pop("user_id")
        return responseDict
    except Exception as e:
        return e

#######################################################
def deleteUserFromOrganization(orgID, baseURL, baseHeader, userMail):
    """
    Ask Auth0 API to delete someone from an organization via their name

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param userMail: userName of person that should be deleted
    :type userMail: str
    :return: If successful or not
    :rtype: True or error
    """
    try:
        header = baseHeader
        header["Cache-Control"] = "no-cache"

        # fetch user id via E-Mail of the user
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/users?q=email:"{userMail}"&search_engine=v3', headers=baseHeader) )
        if isinstance(response, Exception):
            raise response
        userID = response[0]["user_id"]
        # delete person from organization via userID
        data = { "members": [userID]}
        response = handleTooManyRequestsError( lambda : requests.delete(f'{baseURL}/api/v2/organizations/{orgID}/members', headers=header, json=data) )
        if isinstance(response, Exception):
            raise response
        postgres.ProfileManagement.deleteUser("", uID=userID)
        return userID
    except Exception as e:
        return e
    
#######################################################
def createRole(baseURL, baseHeader, roleName, roleDescription):
    """
    Ask Auth0 API to create a new role

    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param roleName: name of role
    :type roleName: str
    :param roleDescription: what the role stands for
    :type roleDescription: str
    :return: If successful the id or an error if not
    :rtype: Dict with ID or error
    """
    try:
        header = baseHeader
        header["Cache-Control"] = "no-cache"

        data = { "name": roleName, "description": roleDescription}
        response = handleTooManyRequestsError( lambda: requests.post(f'{baseURL}/api/v2/roles', headers=header, json=data) )
        if isinstance(response, Exception):
            raise response
        
        return response
    except Exception as e:
        return e

#######################################################
def assignRole(orgID, baseURL, baseHeader, userMail, roleID):
    """
    Assign a role to a person

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param userMail: mail adress of person that should get the role
    :type userMail: str
    :param roleID: ID of the role for that person
    :type roleID: str
    :return: If successful or not
    :rtype: True or error
    """
    try:
        header = baseHeader
        header["Cache-Control"] = "no-cache"

        # fetch user id via E-Mail of the user
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/users?q=email:"{userMail}"&search_engine=v3', headers=baseHeader) )
        if isinstance(response, Exception):
            raise response
        userID = response[0]["user_id"]

        data = { "roles": [roleID]}
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/organizations/{orgID}/members/{userID}/roles', headers=header, json=data) )
        if isinstance(response, Exception):
            raise response

        return userID

    except Exception as e:
        return e
    
#######################################################
def removeRole(orgID, baseURL, baseHeader, userMail, roleID):
    """
    Remove a role from a person

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param userMail: mail adress of person
    :type userMail: str
    :param roleID: ID of the role for that person
    :type roleID: str
    :return: If successful or not
    :rtype: True or error
    """
    try:
        header = baseHeader
        header["Cache-Control"] = "no-cache"

        # fetch user id via E-Mail of the user
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/users?q=email:"{userMail}"&search_engine=v3', headers=baseHeader) )
        if isinstance(response, Exception):
            raise response
        userID = response[0]["user_id"]

        data = { "roles": [roleID]}
        response = handleTooManyRequestsError( lambda : requests.delete(f'{baseURL}/api/v2/organizations/{orgID}/members/{userID}/roles', headers=header, json=data))
        if isinstance(response, Exception):
            raise response
        
        return userID
        
    except Exception as e:
        return e

#######################################################
def editRole(orgID, baseURL, baseHeader, roleID, roleName, roleDescription):
    """
    Ask Auth0 API to edit a role

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param roleID: ID of the role for that person
    :type roleID: str
    :param roleName: name of role
    :type roleName: str
    :param roleDescription: what the role stands for
    :type roleDescription: str
    :return: If successful true or an error if not
    :rtype: Bool or error
    """
    try:
        header = baseHeader
        header["Cache-Control"] = "no-cache"

        data = { "name": roleName, "description": roleDescription}
        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/roles/{roleID}', headers=header, json=data) )
        if isinstance(response, Exception):
            raise response
        
        return True
    except Exception as e:
        return e


#######################################################
def getRoles(orgID, baseURL, baseHeader, orgaName):
    """
    Fetch all roles and filter for the organization

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param orgaName: Name of the organization
    :type orgaName: str
    :return: If successful, list of roles for that organization, error if not
    :rtype: List or error
    """
    try:
        header = baseHeader
        header["Cache-Control"] = "no-cache"
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/roles', headers=header) )
        if isinstance(response, Exception):
            raise response
        roles = response
        rolesOut = []
        for entry in roles:
            if orgaName in entry["name"]:
                entry["name"] = entry["name"].replace(orgaName+"-", "")
                rolesOut.append(entry)
        return rolesOut
    except Exception as e:
        return e

#######################################################
def deleteRole(orgID, baseURL, baseHeader, roleID):
    """
    Delete role via ID

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param roleID: ID of the role that shall be deleted
    :type roleID: str
    :return: If successful, true, error if not
    :rtype: Bool or error
    """
    try:
        response = handleTooManyRequestsError( lambda : requests.delete(f'{baseURL}/api/v2/roles/{roleID}', headers=baseHeader) )
        if isinstance(response, Exception):
            raise response
        return True
        
    except Exception as e:
        return e

#######################################################
def addPermissionsToRole(orgID, baseURL, baseHeader, roleID, listOfPermissionIDs):
    """
    Add Permissions to role

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param roleID: ID of the role that shall be deleted
    :type roleID: str
    :param listOfPermissionIDs: List of permission IDs
    :type listOfPermissionIDs: list
    :return: If successful, true, error if not
    :rtype: Bool or error
    """    
    try:
        header = baseHeader
        header["Cache-Control"] = "no-cache"

        data = {"permissions" : []}
        for entry in listOfPermissionIDs:
            data["permissions"].append({"resource_server_identifier": "back.semper-ki.org", "permission_name": entry})

        response = handleTooManyRequestsError( lambda : requests.post(f'{baseURL}/api/v2/roles/{roleID}/permissions', headers=header, json=data) )
        if isinstance(response, Exception):
            raise response
        return True

    except Exception as e:
        return e

#######################################################
def getAllPermissions(orgID, baseURL, baseHeader):
    """
    Get all Permissions

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :return: If successful, list of permissions for role as array, error if not
    :rtype: JSON or error
    """ 
    try:
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/resource-servers/back.semper-ki.org', headers=baseHeader) )
        if isinstance(response, Exception):
            raise response
        return response["scopes"]

    except Exception as e:
        return e

#######################################################
def getPermissionsForRole(orgID, baseURL, baseHeader, roleID):
    """
    Get Permissions of role

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :param roleID: ID of the role that shall be deleted
    :type roleID: str
    :return: If successful, list of permissions for role as array, error if not
    :rtype: JSON or error
    """    
    try:
        response = handleTooManyRequestsError( lambda : requests.get(f'{baseURL}/api/v2/roles/{roleID}/permissions', headers=baseHeader) )
        if isinstance(response, Exception):
            raise response
        return response

    except Exception as e:
        return e

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
def handleCallToPath(request):
    """
    Ask Auth0 API for various stuff

    :param request: POST request with intent and data
    :type request: HTTP POST
    :return: Response if successful or not
    :rtype: HTTP/JSON Response
    """

    content = json.loads(request.body.decode("utf-8"))["data"]

    # Get token and attach to header that every call needs
    auth0.apiToken.checkIfExpired()
    headers = {
        'authorization': f'Bearer {auth0.apiToken.accessToken}',
        'content-Type': 'application/json'
    }
    baseURL = f"https://{settings.AUTH0_DOMAIN}"
    orgID = request.session["user"]["userinfo"]["org_id"]
    userName = request.session["user"]["userinfo"]["nickname"]

    try:
        if content["intent"] == "addUser":
            emailAdressOfUserToBeAdded = content["content"]["email"]
            result = sendInvite(orgID, baseURL, headers, userName, True, emailAdressOfUserToBeAdded)
            if isinstance(result, Exception):
                raise result
            logger.info(f"{userName} invited the user {emailAdressOfUserToBeAdded} at " + str(datetime.datetime.now()))
            
        elif content["intent"] == "getInviteLink":
            emailAdressOfUserToBeAdded = content["content"]["email"]
            result = sendInvite(orgID, baseURL, headers, userName, False, emailAdressOfUserToBeAdded)
            if isinstance(result, Exception):
                raise result
            else:
                logger.info(f"{userName} invited the user {emailAdressOfUserToBeAdded} at " + str(datetime.datetime.now()))
                return HttpResponse(result["invitation_url"])
            
        elif content["intent"] == "fetchUsers":
            orgaName = getOrganizationName(request.session, orgID, baseURL, headers)
            if isinstance(orgaName, Exception):
                raise orgaName
            result = getMembersOfOrganization(orgID, baseURL, headers, orgaName)
            if isinstance(result, Exception):
                raise result
            else:
                return JsonResponse(result, safe=False)

        elif content["intent"] == "deleteUser":
            emailAdressOfUser = content["content"]["email"]
            result = deleteUserFromOrganization(orgID, baseURL, headers, emailAdressOfUser)
            if isinstance(result, Exception):
                raise result
            retVal = sendEventViaWebsocket(orgID, baseURL, headers, "deleteUserFromOrganization", result)
            if isinstance(retVal, Exception):
                raise retVal
            logger.info(f"{userName} deleted the user {emailAdressOfUserToBeAdded} at " + str(datetime.datetime.now()))

        elif content["intent"] == "createRole":
            orgaName = getOrganizationName(request.session, orgID, baseURL, headers)
            if isinstance(orgaName, Exception):
                raise orgaName
            
            # append organization name to the role name to avoid that two different organizations create the same role
            roleName = orgaName + "-" + content["content"]["roleName"]
            roleDescription = content["content"]["roleDescription"]

            result = createRole(baseURL, headers, roleName, roleDescription)
            if isinstance(result, Exception):
                raise result
            else:
                logger.info(f"{userName} created the role {roleName} at " + str(datetime.datetime.now()))
                return JsonResponse(result, safe=False)
        
        elif content["intent"] == "getRoles":
            orgaName = getOrganizationName(request.session, orgID, baseURL, headers)
            if isinstance(orgaName, Exception):
                raise orgaName
            result = getRoles(orgID, baseURL, headers, orgaName)
            if isinstance(result, Exception):
                raise result
            else:
                return JsonResponse(result, safe=False)

        elif content["intent"] == "assignRole":
            emailAdressOfUser = content["content"]["email"]
            roleID = content["content"]["roleID"]
            result = assignRole(orgID, baseURL, headers, emailAdressOfUser, roleID)
            if isinstance(result, Exception):
                raise result
            retVal = sendEventViaWebsocket(orgID, baseURL, headers, "assignRole", result)
            if isinstance(retVal, Exception):
                raise retVal
            logger.info(f"{userName} assigned the role {roleID} to {emailAdressOfUser} at " + str(datetime.datetime.now()))
            
        elif content["intent"] == "removeRole":
            emailAdressOfUser = content["content"]["email"]
            roleID = content["content"]["roleID"]
            result = removeRole(orgID, baseURL, headers, emailAdressOfUser, roleID)
            if isinstance(result, Exception):
                raise result
            # retVal = sendEventViaWebsocket(orgID, baseURL, headers, "removeRole", result)
            # if isinstance(retVal, Exception):
            #     raise retVal
            logger.info(f"{userName} removed the role {roleID} from {emailAdressOfUser} at " + str(datetime.datetime.now()))
        
        elif content["intent"] == "editRole":
            roleID = content["content"]["roleID"]
            roleName = orgaName + "-" + content["content"]["roleName"]
            roleDescription = content["content"]["roleDescription"]
            result = editRole(orgID, baseURL, headers, roleID, roleName, roleDescription)
            if isinstance(result, Exception):
                raise result
            retVal = sendEventViaWebsocket(orgID, baseURL, headers, "editRole", roleID)
            if isinstance(retVal, Exception):
                raise retVal
            logger.info(f"{userName} edited the role {roleName} at " + str(datetime.datetime.now()))

        elif content["intent"] == "deleteRole":
            roleID = content["content"]["roleID"]
            result = deleteRole(orgID, baseURL, headers, roleID)
            if isinstance(result, Exception):
                raise result
            logger.info(f"{userName} deleted the role {roleID} at " + str(datetime.datetime.now()))

        elif content["intent"] == "getPermissions":
            result = getAllPermissions(orgID, baseURL, headers)
            if isinstance(result, Exception):
                raise result
            else:
                return JsonResponse(result,safe=False)
        
        elif content["intent"] == "getPermissionsForRole":
            roleID = content["content"]["roleID"]
            result = getPermissionsForRole(orgID, baseURL, headers, roleID)
            if isinstance(result, Exception):
                raise result
            else:
                return JsonResponse(result,safe=False)

        elif content["intent"] == "setPermissionsForRole":
            roleID = content["content"]["roleID"]
            permissionList = content["content"]["permissionIDs"]
            result = addPermissionsToRole(orgID, baseURL, headers, roleID, permissionList)
            if isinstance(result, Exception):
                raise result
            retVal = sendEventViaWebsocket(orgID, baseURL, headers, "addPermissionsToRole", roleID)
            if isinstance(retVal, Exception):
                raise retVal
            logger.info(f"{userName} set permissions of role {roleID} at " + str(datetime.datetime.now()))
        else:
            return HttpResponse("Invalid request", status=400)

        return HttpResponse("Success", status=200)
    except Exception as e:
        print(f'Generic Exception: {e}')
        if "many requests" in e.args[0]:
            return HttpResponse("Failed - " + str(e), status=429)
        else:
            return HttpResponse("Failed - " + str(e), status=500)
