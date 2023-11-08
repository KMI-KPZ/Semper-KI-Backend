"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls to manage a user/organization profile
"""
import types, json, enum, re

from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from ...modelFiles.profileModel import User, Organization

from backend_django.utilities import crypto

#TODO: switch to async versions at some point

####################################################################################
# Profile
class ProfileManagementBase():
    ##############################################
    @staticmethod
    def getUser(session):
        """
        Check whether a user exists or not and retrieve entry.

        :param session: session
        :type session: Dictionary
        :return: User details from database
        :rtype: Dictionary

        """
        userID = session["user"]["userinfo"]["sub"]
        obj = {}
        try:
            obj = User.objects.get(subID=userID).toDict()

            if len(obj["organizations"]) !=0:
                if obj["organizations"][0] != "None":
                    for idx, elem in enumerate(obj["organizations"]):
                        obj["organizations"][idx] = Organization.objects.get(subID=elem).hashedID
        except (Exception) as error:
            print(error)

        return obj
    
    ##############################################
    @staticmethod
    def getOrganization(session):
        """
        Check whether an organization exists or not and retrieve information.

        :param session: session
        :type session: Dictionary
        :return: Organization details from database
        :rtype: Dictionary

        """
        orgaID = session["user"]["userinfo"]["org_id"]
        obj = {}
        try:
            obj = Organization.objects.get(subID=orgaID).toDict()
        except (Exception) as error:
            print(error)

        return obj

    ##############################################
    @staticmethod
    def getUserHashID(session):
        """
        Retrieve hashed User ID from Session

        :param session: session
        :type session: Dictionary
        :return: Hashed user key from database
        :rtype: Str

        """
        hashID = ""
        try:
            userID = session["user"]["userinfo"]["sub"]
            hashID = User.objects.get(subID=userID).hashedID
        except (Exception) as error:
            print(error)

        return hashID
    
    ##############################################
    @staticmethod
    def getOrgaHashID(session):
        """
        Retrieve hashed Organization ID from Session

        :param session: session
        :type session: Dictionary
        :return: Hashed user key from database
        :rtype: Str

        """
        hashID = ""
        try:
            if "org_id" in session["user"]["userinfo"]:
                orgID = session["user"]["userinfo"]["org_id"]
                hashID = Organization.objects.get(subID=orgID).hashedID
        except (Exception) as error:
            print(error)

        return hashID
    
    ##############################################
    @staticmethod
    def getUserKeyViaHash(hashedID):
        """
        Retrieve User ID via Database and hashkey

        :param hashedID: hashed ID
        :type hashedID: str
        :return: Orga key from database
        :rtype: Str

        """
        IDOfUserOrOrga = ""
        try:
            IDOfUserOrOrga = Organization.objects.get(hashedID=hashedID).subID
        except (ObjectDoesNotExist) as error:
            IDOfUserOrOrga = User.objects.get(hashedID=hashedID).subID
        except (Exception) as error:
            print(error)

        return IDOfUserOrOrga
    
    ##############################################
    @staticmethod
    def getUserViaHash(hashedID):
        """
        Retrieve User Object via Database and hashkey

        :param hashedID: hashed ID
        :type hashedID: str
        :return: Dict from database
        :rtype: Dict

        """
        ObjOfUserOrOrga = ""
        try:
            ObjOfUserOrOrga = Organization.objects.get(hashedID=hashedID)
        except (ObjectDoesNotExist) as error:
            ObjOfUserOrOrga = User.objects.get(hashedID=hashedID)
        except (Exception) as error:
            print(error)

        return ObjOfUserOrOrga

    ##############################################
    @staticmethod
    def getUserKey(session):
        """
        Retrieve User ID from Session

        :param session: session
        :type session: Dictionary
        :return: User key from database
        :rtype: Str

        """
        userID = ""
        try:
            userID = session["user"]["userinfo"]["sub"]
        except (Exception) as error:
            print(error)

        return userID
    
    ##############################################
    @staticmethod
    def getUserOrgaKey(session):
        """
        Retrieve User ID from Session

        :param session: session
        :type session: Dictionary
        :return: User key from database
        :rtype: Str

        """
        orgaID = ""
        try:
            if "org_id" in session["user"]["userinfo"]:
                orgaID = session["user"]["userinfo"]["org_id"]
        except (Exception) as error:
            print(error)

        return orgaID

    ##############################################
    @staticmethod
    def getUserKeyWOSC(session=None, uID=None):
        """
        Retrieve User ID from Session without special characters

        :param session: session
        :type session: Dictionary
        :return: User key from database without stuff like | or ^
        :rtype: Str

        """
        userID = ""
        try:
            if session is not None:
                userID = session["user"]["userinfo"]["sub"]
            if uID is not None:
                userID = uID
            userID = re.sub(r"[^a-zA-Z0-9]", "", userID)
        except (Exception) as error:
            print(error)

        return userID
    
    ##############################################
    @staticmethod
    def setLoginTime(userIDHash):
        """
        Sets the las login Time to now. Used for 'Last Login'.

        :param session: userID
        :type session: str
        :return: Nothing
        :rtype: None

        """
        currUser = User.objects.get(hashedID=userIDHash)
        currUser.lastSeen = timezone.now()
        currUser.save()

    ##############################################
    @staticmethod
    def deleteUser(session, uHashedID=""):
        """
        Delete User.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        try:
            if uHashedID != "":
                affected = User.objects.filter(hashedID=uHashedID).delete()
            else:
                affected = User.objects.filter(subID=session["user"]["userinfo"]["sub"]).delete()
        except (Exception) as error:
            print(error)
            return False
        return True
    
    ##############################################
    @staticmethod
    def deleteOrganization(session, orgID=""):
        """
        Delete Organization.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        try:
            if orgID != "":
                affected = Organization.objects.filter(hashedID=orgID).delete()
            else:
                affected = Organization.objects.filter(subID=session["user"]["userinfo"]["org_id"]).delete()
            
        except (Exception) as error:
            print(error)
            return False
        return True
    
    ##############################################
    @staticmethod
    def getAll():
        """
        Get all Users and Organizations.

        :return: Two arrays containing all entries
        :rtype: List, List

        """
        userList = []
        orgaList = []
        for user in User.objects.all():
            userList.append(user.toDict())
        for orga in Organization.objects.all():
            orgaList.append(orga.toDict())
        return userList, orgaList

####################################################################################
class ProfileManagementUser(ProfileManagementBase):

    ##############################################
    @staticmethod
    def addUserIfNotExists(session, organization=None):
        """
        Add user if the entry doesn't already exists.

        :param session: POST request session
        :type session: Dictionary
        :param organization: Dummy object to comply to interface of function with same name from sister class
        :type organization: None
        :return: Information about the user. Necessary to check if database entry is equal to callback information
        :rtype: User Object

        """

        userID = session["user"]["userinfo"]["sub"]
        try:
            # first get, then create
            result = User.objects.get(subID=userID)

            return result

        except (ObjectDoesNotExist) as error:
            try:
                userName = session["user"]["userinfo"]["nickname"]
                userEmail = session["user"]["userinfo"]["email"]
                details = {}
                updated = timezone.now()
                lastSeen = timezone.now()
                idHash = crypto.generateSecureID(userID)
                 
                createdUser = User.objects.create(subID=userID, hashedID=idHash, name=userName, email=userEmail, organizations=["None"], details=details, updatedWhen=updated, lastSeen=lastSeen)

                return createdUser
            except (Exception) as error:
                print(error)
                return error

    ##############################################
    @staticmethod
    def updateContent(session, details, userID=""):
        """
        Update user details.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        if userID == "":
            subID = session["user"]["userinfo"]["sub"]
        else:
            subID = userID
        updated = timezone.now()
        try:
            existingObj = User.objects.get(subID=subID)
            existingInfo = {"name": existingObj.name, "details": existingObj.details, "email": existingObj.email}
            for key in details:
                existingInfo[key] = details[key]
            affected = User.objects.filter(subID=subID).update(details=existingInfo["details"], name=existingInfo["name"], email=existingInfo["email"], updatedWhen=updated)
        except (Exception) as error:
            print(error)
            return False
        return True
    
    ##############################################
    @staticmethod
    def getClientID(session):
        """
        Get ID of current client (can be organization or user)
        :param session: request session
        :type session: dict
        :return: hashed ID
        :rtype: String

        """
        return ProfileManagementUser.getUserHashID(session)

####################################################################################
class ProfileManagementOrganization(ProfileManagementBase):

    ##############################################
    @staticmethod
    def getAllContractors():
        """
        Get all contractors.
        
        :return: All contractors
        :rtype: Dictionary

        """
        obj = {}
        try:
            listOfManufacturers = Organization.objects.filter(canManufacture=True)
            returnValue = []
            for entry in listOfManufacturers:
                returnValue.append({"hashedID": entry.hashedID, "name": entry.name, "details": entry.details})
        except (Exception) as error:
            print(error)

        return returnValue

    ##############################################
    @staticmethod
    def addUserIfNotExists(session, organization):
        """
        Add user if the entry doesn't already exists.

        :param session: POST request session
        :type session: Dictionary
        :return: User info for verification
        :rtype: User object

        """

        userID = session["user"]["userinfo"]["sub"]
        try:
            # first get, then create
            result = User.objects.get(subID=userID)
            return result
        except (ObjectDoesNotExist) as error:
            try:
                userName = session["user"]["userinfo"]["nickname"]
                userEmail = session["user"]["userinfo"]["email"]
                details = {}
                updated = timezone.now()
                lastSeen = timezone.now()
                idHash = crypto.generateSecureID(userID)
                 

                createdUser = User.objects.create(subID=userID, hashedID=idHash, name=userName, email=userEmail, organizations=[organization.subID], details=details, updatedWhen=updated, lastSeen=lastSeen)
                if ProfileManagementOrganization.addUserToOrganization(createdUser, session["user"]["userinfo"]["org_id"]) == False:
                    raise Exception(f"User could not be added to organization!, {createdUser}, {organization}")
                
                return createdUser
            except (Exception) as error:
                print(error)
                return error

    ##############################################
    @staticmethod
    def addUserToOrganization(userToBeAdded, organizationID):
        """
        Add user to organization.

        :param userToBeAdded: User to be added
        :type userToBeAdded: User
        :param organization: id of the organization
        :type organization: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        try:
            result = Organization.objects.get(subID=organizationID)
            result.users.add(userToBeAdded)
        except (ObjectDoesNotExist) as error:
            print("Organization doesn't exist!", error)
            return False

        return True

    ##############################################
    @staticmethod
    def addOrGetOrganization(session):
        """
        Add organization if the entry doesn't already exists.

        :param session: POST request session
        :type session: Dictionary
        :param typeOfOrganization: type of the organization, can be: manufacturer, stakeholder
        :type typeOfOrganization: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        orgaID = session["user"]["userinfo"]["org_id"]
        updated = timezone.now()
        try:
            # first get, then create
            resultObj = Organization.objects.get(subID=orgaID)
            return resultObj
        except (ObjectDoesNotExist) as error:
            try:
                orgaName = session["organizationName"]
                orgaDetails = {"email": "", "adress": "", "taxID": ""}
                idHash = crypto.generateSecureID(orgaID)
                uri = ""
                resultObj = Organization.objects.create(subID=orgaID, hashedID=idHash, name=orgaName, details=orgaDetails, uri=uri, updatedWhen=updated) 
                return resultObj
            except (Exception) as error:
                print(error)
                return None
        except (Exception) as error:
            print(error)
            return None

    ##############################################
    @staticmethod
    def updateContent(session, details, orgaID=""):
        """
        Update user details and more.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        if orgaID == "":
            orgID = session["user"]["userinfo"]["org_id"]
        else:
            orgID = orgaID
        updated = timezone.now()
        try:
            existingObj = Organization.objects.get(subID=orgID)
            existingInfo = {"details": existingObj.details, "canManufacture": existingObj.canManufacture, "name": existingObj.name, "uri": existingObj.uri}
            for key in details:
                existingInfo[key] = details[key]
            affected = Organization.objects.filter(subID=orgID).update(details=existingInfo["details"], canManufacture=existingInfo["canManufacture"], name=existingInfo["name"], uri=existingInfo["uri"], updatedWhen=updated)
        except (Exception) as error:
            print(error)
            return False
        return True

    ##############################################
    @staticmethod
    def getClientID(session):
        """
        Get ID of current client (can be organization or user)
        :param session: request session
        :type session: dict
        :return: hashed ID
        :rtype: String

        """
        return ProfileManagementBase.getOrganization(session)["hashedID"]

profileManagement= {"user": ProfileManagementUser(), "organization": ProfileManagementOrganization()}