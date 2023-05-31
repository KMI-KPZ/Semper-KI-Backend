"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling of admin requests for organizations, api calls to auth0
"""

import json, requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from ..services import auth0, postgres

#######################################################
def getOrganizationName(orgID, baseURL, baseHeader):
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
        res = requests.get(f'{baseURL}/api/v2/organizations/{orgID}', headers=baseHeader)
        return res.json()["display_name"]
    except Exception as e:
        return e

#######################################################
def sendInvite(orgID, baseURL, baseHeader, nameOfCurrentUser, withEmail, emailAdressOfUserToBeAdded=""):
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

            response = requests.post(f'{baseURL}/api/v2/organizations/{orgID}/invitations', headers=header, json=data)
            return True
        else:
            data["send_invitation_email"] = False

            response = requests.post(f'{baseURL}/api/v2/organizations/{orgID}/invitations', headers=header, json=data)
            return response.json()
    except Exception as e:
        return e

#######################################################
def getMembersOfOrganization(orgID, baseURL, baseHeader):
    """
    Ask Auth0 API to invite someone via e-mail

    :param orgID: the id of the current organization
    :type orgID: str
    :param baseURL: start of the url
    :type baseURL: str
    :param baseHeader: Header with basic stuff
    :type baseHeader: Dict
    :return: If successful or not
    :rtype: Json or error
    """
    try:
        response = requests.get(f'{baseURL}/api/v2/organizations/{orgID}/members', headers=baseHeader)
        responseDict = response.json()
        for entry in responseDict:
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
        response = requests.get(f'{baseURL}/api/v2/users?q=email:"{userMail}"&search_engine=v3', headers=baseHeader)
        userID = response.json()[0]["user_id"]
        # delete person from organization via userID
        data = { "members": [userID]}
        response = requests.delete(f'{baseURL}/api/v2/organizations/{orgID}/members', headers=header, json=data)
        if response.status_code == 204:
            # delete user from database as well
            postgres.ProfileManagement.deleteUser("", uID=userID)
            return True
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
        response = requests.post(f'{baseURL}/api/v2/roles', headers=header, json=data)
        roleInfo = response.json()
        if response.status_code == 200:
            return roleInfo
        else:
            raise response.text
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
        response = requests.get(f'{baseURL}/api/v2/users?q=email:"{userMail}"&search_engine=v3', headers=baseHeader)
        userID = response.json()[0]["user_id"]

        data = { "roles": [roleID]}
        response = requests.post(f'{baseURL}/api/v2/organizations/{orgID}/members/{userID}/roles', headers=header, json=data)
        if response.status_code == 204:
            return True
        else:
            raise response.text
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
        response = requests.get(f'{baseURL}/api/v2/roles', headers=header)
        roles = response.json()
        rolesOut = []
        for entry in roles:
            if orgaName in entry["name"]:
                rolesOut.append(entry)
        return rolesOut
    except Exception as e:
        return e

#######################################################
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
            
        elif content["intent"] == "fetchUsers":
            result = getMembersOfOrganization(orgID, baseURL, headers)
            if isinstance(result, Exception):
                raise result
            else:
                return JsonResponse(result)

        elif content["intent"] == "deleteUser":
            emailAdressOfUser = content["content"]["email"]
            result = deleteUserFromOrganization(orgID, baseURL, headers, emailAdressOfUser)
            if isinstance(result, Exception):
                raise result

        elif content["intent"] == "createRole":
            orgaName = getOrganizationName(orgID, baseURL, headers)
            if isinstance(orgaName, Exception):
                raise orgaName
            
            # append organization name to the role name to avoid that two different organizations create the same role
            roleName = orgaName + "-" + content["content"]["roleName"]
            roleDescription = content["content"]["roleDescription"]

            result = createRole(baseURL, headers, roleName, roleDescription)
            if isinstance(result, Exception):
                raise result
            else:
                return JsonResponse(result)
        
        elif content["intent"] == "getRoles":
            orgaName = getOrganizationName(orgID, baseURL, headers)
            if isinstance(orgaName, Exception):
                raise orgaName
            result = getRoles(orgID, baseURL, headers, orgaName)
            if isinstance(result, Exception):
                raise result
            else:
                return JsonResponse(result)

        elif content["intent"] == "assignRole":
            emailAdressOfUser = content["content"]["email"]
            roleID = content["content"]["roleID"]
            result = assignRole(orgID, baseURL, headers, emailAdressOfUser, roleID)
            if isinstance(result, Exception):
                raise result
            
        elif content["intent"] == "getInviteLink":
            result = sendInvite(orgID, baseURL, headers, userName, False)
            if isinstance(result, Exception):
                raise result
            else:
                return HttpResponse(result["invitation_url"])
            
        return HttpResponse("Success", status=200)
    except Exception as e:
        print(f'Generic Exception: {e}')
        return HttpResponse("Failed", status=500)
    