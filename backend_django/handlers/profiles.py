import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import psycopg2
from django.db import models
from django.utils import timezone

from ..modelFiles.profile import Profile
#from ..models import Profile

#TODO: switch to async versions at some point

##############################################
def getUser(request):
    """
    Check whether a user exists or not.

    :param request: GET request
    :type request: HTTP GET
    :return: User details from database
    :rtype: Dictionary

    """
    userName = request.session["user"]["userinfo"]["nickname"]
    obj = {}
    try:
        obj = Profile.objects.get(name=userName).toDict()
    except (Exception) as error:
        print(error)

    return obj

def getUserTest(request):
    """
    Same as getUser but for testing.

    :param request: GET request
    :type request: HTTP GET
    :return: User details from database
    :rtype: JSON

    """
    return JsonResponse(getUser(request))

##############################################
def addUser(request):
    """
    Add user if the entry doesn't already exists.

    :param request: POST request with session
    :type request: HTTP POST
    :return: HTTP response (only used for tests)
    :rtype: HTTP Status

    """
    userName = request.session["user"]["userinfo"]["nickname"]
    userEmail = request.session["user"]["userinfo"]["email"]
    userType = "user"
    updated = timezone.now()
    try:
        obj, created = Profile.objects.get_or_create(name=userName, email=userEmail, role=userType, defaults={'updatedWhen': updated})
        
    except (Exception) as error:
        print(error)
        return HttpResponse(error, status=500)
    return HttpResponse("Worked")

##############################################
def updateUser(request):
    """
    Update user details.

    :param request: GET request
    :type request: HTTP GET
    :return: HTTP response
    :rtype: HTTP status

    """
    userName = request.session["user"]["userinfo"]["nickname"]
    userEmail = request.session["user"]["userinfo"]["email"]
    userType = "user"
    updated = timezone.now()
    try:
        affected = Profile.objects.filter(name=userName).update(email=userEmail, role=userType, updatedWhen=updated)
        
    except (Exception) as error:
        print(error)
        return HttpResponse(error, status=500)
    return HttpResponse("Worked")

##############################################
def deleteUser(request):
    """
    Deletes an entry in the database corresponding to user name.

    :param request: DELETE request
    :type request: HTTP DELETE
    :return: HTTP response
    :rtype: HTTP status

    """
    userName = request.session["user"]["userinfo"]["nickname"]
    try:
        affected = Profile.objects.filter(name=userName).delete()
        
    except (Exception) as error:
        print(error)
        return HttpResponse(error, status=500)
    return HttpResponse("Worked")

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