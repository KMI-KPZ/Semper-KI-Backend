"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling of database requests
"""

import datetime
import json, os, logging
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import psycopg2
from django.db import models
from django.utils import timezone
from urllib.parse import unquote
from django.views.decorators.http import require_http_methods

from ..handlers import basics

from ..services.postgresDB import pgProfiles

logger = logging.getLogger(__name__)
##############################################
# @checkIfUserIsLoggedIn()
# @require_http_methods(["GET"])
# def addUserTest(request):
#     """
#     Same as addUser but for testing.

#     :param request: GET request
#     :type request: HTTP GET
#     :return: HTTP response
#     :rtype: HTTP status

#     """

#     flag = request.session["pgProfileClass"].addUserIfNotExists(request.session)
#     if flag is True:
#         return HttpResponse("Worked")
#     else:
#         return HttpResponse("Failed", status=500)


##############################################
# @checkIfUserIsLoggedIn()
# @require_http_methods(["GET"])
# def getUserTest(request):
#     """
#     Same as getUser but for testing.

#     :param request: GET request
#     :type request: HTTP GET
#     :return: User details from database
#     :rtype: JSON

#     """
#     return JsonResponse(pgProfiles.ProfileManagement.getUser(request.session))

#######################################################
@basics.checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
def getOrganisationDetails(request):
    """
    Return details about organisation. 

    :param request: GET request
    :type request: HTTP GET
    :return: Organisation details
    :rtype: Json

    """
    # Read organisation details from Database
    return JsonResponse(pgProfiles.ProfileManagementBase.getOrganisation(request.session))

##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"])
@basics.checkIfRightsAreSufficient()
def updateDetailsOfOrganisation(request):
    """
    Update details of organisation of that user.

    :param request: PATCH request
    :type request: HTTP PATCH
    :return: HTTP response
    :rtype: HTTP status

    """

    content = json.loads(request.body.decode("utf-8"))
    logger.info(f"{pgProfiles.ProfileManagementBase.getUser(request.session)['name']} updated details of their organisation to {content['details']} at " + str(datetime.datetime.now()))
    flag = pgProfiles.ProfileManagementOrganisation.updateDetails(request.session, content["details"])
    if flag is True:
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)

##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["DELETE"])
@basics.checkIfRightsAreSufficient()
def deleteOrganisation(request):
    """
    Deletes an entry in the database corresponding to user name.

    :param request: DELETE request
    :type request: HTTP DELETE
    :return: HTTP response
    :rtype: HTTP status

    """
    logger.info(f"{pgProfiles.ProfileManagementBase.getUser(request.session)['name']} deleted organisation {pgProfiles.ProfileManagementOrganisation.getOrganisation(request.session)['name']} at " + str(datetime.datetime.now()))
    flag = pgProfiles.ProfileManagementBase.deleteOrganisation(request.session)
    if flag is True:
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)

##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["DELETE"])
def deleteOrganisationAsAdmin(request):
    """
    Deletes an entry in the database corresponding to orga id.

    :param request: DELETE request
    :type request: HTTP DELETE
    :return: HTTP response
    :rtype: HTTP status

    """
    if request.session["usertype"] == "admin":
        content = json.loads(request.body.decode("utf-8"))
        orgaID = content["hashedID"]
        orgaName = content["name"]

        flag = pgProfiles.ProfileManagementBase.deleteOrganisation(request.session, orgaID)
        if flag is True:
            logger.info(f"Admin {request.session['user']['userinfo']['nickname']} deleted organisation {orgaName} at " + str(datetime.datetime.now()))
            return HttpResponse("Worked")
        else:
            return HttpResponse("Failed", status=500)
    else:
        return HttpResponse("Not an admin!", status=401)

##############################################################################################################

#######################################################
@basics.checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
def getUserDetails(request):
    """
    Return details about user. 

    :param request: GET request
    :type request: HTTP GET
    :return: User details
    :rtype: Json

    """
    # Read user details from Database
    return JsonResponse(pgProfiles.ProfileManagementBase.getUser(request.session))

##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"])
def updateDetails(request):
    """
    Update user details.

    :param request: PATCH request
    :type request: HTTP PATCH
    :return: HTTP response
    :rtype: HTTP status

    """

    content = json.loads(request.body.decode("utf-8"))
    logger.info(f"{pgProfiles.ProfileManagementBase.getUser(request.session)['name']} updated their details to {content['details']} at " + str(datetime.datetime.now()))
    flag = pgProfiles.ProfileManagementUser.updateDetails(request.session, content["details"])
    if flag is True:
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)
    

##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["DELETE"])
def deleteUser(request):
    """
    Deletes an entry in the database corresponding to user name.

    :param request: DELETE request
    :type request: HTTP DELETE
    :return: HTTP response
    :rtype: HTTP status

    """
    logger.info(f"{pgProfiles.ProfileManagementBase.getUser(request.session)['name']} deleted themselves at " + str(datetime.datetime.now()))
    flag = pgProfiles.ProfileManagementUser.deleteUser(request.session)
    if flag is True:
        return HttpResponse("Worked")
    else:
        return HttpResponse("Failed", status=500)

##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["DELETE"])
def deleteUserAsAdmin(request):
    """
    Deletes an entry in the database corresponding to user id.

    :param request: DELETE request
    :type request: HTTP DELETE
    :return: HTTP response
    :rtype: HTTP status

    """
    if request.session["usertype"] == "admin":
        content = json.loads(request.body.decode("utf-8"))
        userID = content["hashedID"]
        userName = content["name"]

        flag = pgProfiles.ProfileManagementUser.deleteUser(request.session, userID)
        if flag is True:
            logger.info(f"Admin {request.session['user']['userinfo']['nickname']} deleted {userName} at " + str(datetime.datetime.now()))
            return HttpResponse("Worked")
        else:
            return HttpResponse("Failed", status=500)
    else:
        return HttpResponse("Not an admin!", status=401)


##############################################
@basics.checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
def getAll(request):
    """
    Drop all information (of the DB) about all users for admin view.

    :param request: GET request
    :type request: HTTP GET
    :return: JSON response containing all entries of users
    :rtype: JSON Respone

    """
    if request.session["usertype"] == "admin":
        # get all information if you're an admin
        users, organisations = pgProfiles.ProfileManagementBase.getAll()
        outLists = { "user" : users, "organisations": organisations }
        logger.info(f"Admin {request.session['user']['userinfo']['nickname']} fetched all users and orgas at " + str(datetime.datetime.now()))
        return JsonResponse(outLists, safe=False)
    else:
        return HttpResponse("Not an admin!", status=401)

# ##############################################
# def updateUser(request):
#     """
#     Update user details.

#     :param request: GET request
#     :type request: HTTP GET
#     :return: HTTP response
#     :rtype: HTTP status

#     """
#     if "user" in request.session:
#         userID = request.session["user"]["userinfo"]["sub"]
#         userName = request.session["user"]["userinfo"]["nickname"]
#         userEmail = request.session["user"]["userinfo"]["email"]
#         userType = request.session["usertype"]
#         updated = timezone.now()
#         try:
#             affected = Profile.objects.filter(subID=userID).update(name=userName, email=userEmail, role=userType, updatedWhen=updated)
            
#         except (Exception) as error:
#             print(error)
#             return HttpResponse(error, status=500)
#         return HttpResponse("Worked")
#     else:
#         return HttpResponse("Failed", status=401)

##############################################
# def makeAdmin(request):
#     """
#     Make user an admin if the passphrase is correct.

#     :param request: POST request
#     :type request: HTTP POST
#     :return: HTTP response
#     :rtype: HTTP status

#     """
#     if request.method == "POST":
#         if "user" in request.session:
#             if "numberOfTriesToBeAdmin" in request.session:
#                 if request.session["numberOfTriesToBeAdmin"] > 10:
#                     return HttpResponse("Too many tries!", status=429)
#                 else:
#                     request.session["numberOfTriesToBeAdmin"] += 1
#             else:
#                 request.session["numberOfTriesToBeAdmin"] = 1
#             body = request.body.decode("UTF-8")
#             passphraseIndex = body.find("passphrase")
#             passphrase = unquote(body[passphraseIndex:].lstrip("passphrase="))
#             if passphrase == os.environ.get("DJANGO_SECRET"):
#                 userID = request.session["user"]["userinfo"]["sub"]
#                 updated = timezone.now()
#                 try:
#                     Profile.objects.filter(subID=userID).update(role="admin", updatedWhen=updated)
#                 except (Exception) as error:
#                     print(error)
#                     return HttpResponse(error, status=500)
#                 return HttpResponse("Worked")
#             else:
#                 return HttpResponse("Wrong password", status=403)
#         else:
#             return HttpResponse("Not logged in", status=401)
#     return HttpResponse("Wrong method", status=405)


# #############################################################
# dbSettings = {
#     "host": settings.DATABASES["default"]["HOST"],
#     "database": "postgres",
#     "user": settings.DATABASES["default"]["USER"],
#     "password": settings.DATABASES["default"]["PASSWORD"],
#     "port": settings.DATABASES["default"]["PORT"],
# }

# def checkConnection(request):
#     """ Connect to the PostgreSQL database server """
#     conn = None
#     try:
#         # connect to the PostgreSQL server
#         print('Connecting to the PostgreSQL database...')
#         conn = psycopg2.connect(**dbSettings)
		
#         # create a cursor
#         cur = conn.cursor()
        
# 	    # execute a statement
#         print('PostgreSQL database version:')
#         cur.execute('SELECT version()')

#         # display the PostgreSQL database server version
#         db_version = cur.fetchone()
#         print(db_version)
       
# 	    # close the communication with the PostgreSQL
#         cur.close()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#         return HttpResponse(error, status=500)
#     finally:
#         if conn is not None:
#             conn.close()
#             print('Database connection closed.')
    
#     return HttpResponse("Worked")

# ##############################################
# def createTable(request):
#     """ create tables in the PostgreSQL database"""
#     # TODO get name of db from request
#     commands = (
#         """
#         CREATE TABLE profiles (
#             name VARCHAR(255) PRIMARY KEY,
#             email VARCHAR(255) NOT NULL,
#             type VARCHAR(255) NOT NULL
#         )
#         """,
#     )
#     conn = None
#     try:
#         # read the connection parameters
#         # connect to the PostgreSQL server
#         config = dbSettings
#         conn = psycopg2.connect(**config)
#         cur = conn.cursor()
#         # create table one by one
#         for command in commands:
#             cur.execute(command)
#         # close communication with the PostgreSQL database server
#         cur.close()
#         # commit the changes
#         conn.commit()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#         return HttpResponse(error, status=500)
#     finally:
#         if conn is not None:
#             conn.close()
#     return HttpResponse("Worked")


# ##############################################
# # profile is in json format
# def insertUser(profile):
#     name = "testguy" #profile["nickname"]
#     email = "testguy@test.com" #profile["email"]
#     typeOfUser = "user" #profile["role"]


#     sql = """INSERT INTO profiles(name,email,type)
#     VALUES(%s,%s,%s);"""
#     conn = None
#     try:
#         # read database configuration
#         params = dbSettings
#         # connect to the PostgreSQL database
#         conn = psycopg2.connect(**params)
#         # create a new cursor
#         cur = conn.cursor()
#         # execute the INSERT statement
#         cur.execute(sql, (name,email,typeOfUser,))
#         # get the generated id back
#         # student_id = cur.fetchone()[0]
#         # commit the changes to the database
#         conn.commit()
#         # close communication with the database
#         cur.close()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#         return HttpResponse(error, status=500)
#     finally:
#         if conn is not None:
#             conn.close()
    
#     return HttpResponse("Worked")

# ##############################################
# # profile is in json format
# def updateUser(profile):
#     name = "testguy" #profile["nickname"]
#     email = "testguy@test.com" #profile["email"]
#     typeOfUser = "user" #profile["role"]


#     sql = """UPDATE profiles SET (email,type) WHERE name=
#     VALUES(%s,%s);"""
#     conn = None
#     try:
#         # read database configuration
#         params = dbSettings
#         # connect to the PostgreSQL database
#         conn = psycopg2.connect(**params)
#         # create a new cursor
#         cur = conn.cursor()
#         # execute the INSERT statement
#         cur.execute(sql, (name,email,typeOfUser,))
#         # get the generated id back
#         # student_id = cur.fetchone()[0]
#         # commit the changes to the database
#         conn.commit()
#         # close communication with the database
#         cur.close()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#         return HttpResponse(error, status=500)
#     finally:
#         if conn is not None:
#             conn.close()
    
#     return HttpResponse("Worked")