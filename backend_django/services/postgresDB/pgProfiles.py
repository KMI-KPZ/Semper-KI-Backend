"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls to manage a user/organisation profile
"""
import types, json, enum, re

from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from ...modelFiles.profileModel import User, Organization

from backend_django.services import crypto

#TODO: switch to async versions at some point

####################################################################################
# Profile
class ProfileManagementBase():
    ##############################################
    @staticmethod
    def getUser(session):
        """
        Check whether a user exists or not.

        :param session: session
        :type session: Dictionary
        :return: User details from database
        :rtype: Dictionary

        """
        userID = session["user"]["userinfo"]["sub"]
        obj = {}
        try:
            obj = User.objects.get(subID=userID).toDict()
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
    def deleteUser(session, uID=""):
        """
        Delete User.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        if uID != "":
            userID = uID
        else:
            userID = session["user"]["userinfo"]["sub"]
            
        try:
            affected = User.objects.filter(subID=userID).delete()
        except (Exception) as error:
            print(error)
            return False
        return True
    

####################################################################################
class ProfileManagementUser(ProfileManagementBase):

    ##############################################
    @staticmethod
    def addUserIfNotExists(session, organization=None):
        """
        Add user if the entry doesn't already exists.

        :param session: POST request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """

        userID = session["user"]["userinfo"]["sub"]
        try:
            # first get, then create
            result = User.objects.get(subID=userID)
        except (ObjectDoesNotExist) as error:
            try:
                userName = session["user"]["userinfo"]["nickname"]
                userEmail = session["user"]["userinfo"]["email"]
                details = {}
                updated = timezone.now()
                lastSeen = timezone.now()
                idHash = crypto.generateSecureID(userID)
                 
                createdUser = User.objects.create(subID=userID, hashedID=idHash, name=userName, email=userEmail, organizations=["None"], details=details, updatedWhen=updated, lastSeen=lastSeen)

            except (Exception) as error:
                print(error)
                return False
            pass
        return True

    ##############################################
    @staticmethod
    def updateDetails(session, details):
        """
        Update user details.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        userID = session["user"]["userinfo"]["sub"]
        updated = timezone.now()
        try:
            affected = User.objects.filter(subID=userID).update(details=details, updatedWhen=updated)
        except (Exception) as error:
            print(error)
            return False
        return True
    

####################################################################################
class ProfileManagementOrganisation(ProfileManagementBase):
    
    ##############################################
    @staticmethod
    def getAllManufacturers():
        """
        Get all manufacturers.
        
        :return: All manufacturers
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
        :return: Flag if it worked or not
        :rtype: Bool

        """

        userID = session["user"]["userinfo"]["sub"]
        try:
            # first get, then create
            result = User.objects.get(subID=userID)
        except (ObjectDoesNotExist) as error:
            try:
                userName = session["user"]["userinfo"]["nickname"]
                userEmail = session["user"]["userinfo"]["email"]
                details = {}
                updated = timezone.now()
                lastSeen = timezone.now()
                idHash = crypto.generateSecureID(userID)
                 

                createdUser = User.objects.create(subID=userID, hashedID=idHash, name=userName, email=userEmail, organizations=[organization.subID], details=details, updatedWhen=updated, lastSeen=lastSeen)
                if ProfileManagementOrganisation.addUserToOrganization(createdUser, session["user"]["userinfo"]["org_id"]) == False:
                    raise Exception(f"User could not be added to organization!, {createdUser}, {organization}")
                
            except (Exception) as error:
                print(error)
                return False
            pass
        return True

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
                orgaDetails = {"e-mail": "", "adress": "", "taxID": ""}
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
    def updateDetails(session, details):
        """
        Update user details.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        orgID = session["user"]["userinfo"]["org_id"]
        updated = timezone.now()
        try:
            affected = Organization.objects.filter(subID=orgID).update(details=details, updatedWhen=updated)
        except (Exception) as error:
            print(error)
            return False
        return True


pgPBase = ProfileManagementBase()
pgPUser = ProfileManagementUser()
pgPOrganisation = ProfileManagementOrganisation()