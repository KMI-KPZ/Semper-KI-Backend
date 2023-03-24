"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls
"""

from django.utils import timezone

from ..modelFiles.profile import Profile
#from ..models import Profile

#TODO: switch to async versions at some point

##############################################
def getUser(session):
    """
    Check whether a user exists or not.

    :param request: session
    :type request: Dictionary
    :return: User details from database
    :rtype: Dictionary

    """
    userID = session["user"]["userinfo"]["sub"]
    obj = {}
    try:
        obj = Profile.objects.get(subID=userID).toDict()
    except (Exception) as error:
        print(error)

    return obj

##############################################
def addUser(session):
    """
    Add user if the entry doesn't already exists.

    :param request: POST request session
    :type request: Dictionary
    :return: Flag if it worked or not
    :rtype: Bool

    """
    userID = session["user"]["userinfo"]["sub"]
    userName = session["user"]["userinfo"]["nickname"]
    userEmail = session["user"]["userinfo"]["email"]
    userType = session["usertype"]
    updated = timezone.now()
    try:
        # first get, then create
        result = Profile.objects.get(subID=userID)
        if result.role != userType:
            Profile.objects.filter(subID=userID).update(role=userType)
    except (Exception) as error:
        try:
            Profile.objects.create(subID=userID, name=userName, email=userEmail, role=userType, updatedWhen=updated) 
        except (Exception) as error:
            print(error)
            return False
        pass
    return True

##############################################
def updateRole(session):
    """
    Update user role.

    :param request: GET request session
    :type request: Dictionary
    :return: Flag if it worked or not
    :rtype: Bool

    """
    userID = session["user"]["userinfo"]["sub"]
    userType = session["usertype"]
    if userType == "admin": # disallow admin
        print("Getting to be an admin this way is not allowed!")
        return False

    updated = timezone.now()
    try:
        affected = Profile.objects.filter(subID=userID).update(role=userType, updatedWhen=updated)
    except (Exception) as error:
        print(error)
        return False
    return True

##############################################
def deleteUser(session):
    """
    Delete User.

    :param request: GET request session
    :type request: Dictionary
    :return: Flag if it worked or not
    :rtype: Bool

    """
    userID = session["user"]["userinfo"]["sub"]
    try:
        affected = Profile.objects.filter(subID=userID).delete()
    except (Exception) as error:
        print(error)
        return False
    return True