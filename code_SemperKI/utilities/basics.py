"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Basic stuff like decorators and such that is imported in Semper KI
"""

import json

from functools import wraps
from django.http import HttpResponse, JsonResponse

from rest_framework import serializers
from rest_framework.versioning import AcceptHeaderVersioning
from rest_framework.response import Response
from rest_framework import status

from Generic_Backend.code_General.definitions import SessionContent
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase, profileManagement
import code_SemperKI.connections.content.postgresql.pgProcesses as PGProcesses

#######################################################
def manualCheckIfUserMaySeeProject(session, userID:str, projectID:str) -> bool:
    """
    Look for all users of the project and check if they are allowed to see it

    :param userID: The hashID of the user
    :type userID: str
    :param projectID: The projectID of the project in question
    :type projectID: str
    :return: True if the user belongs to the rightful, false if not
    :rtype: Bool

    """
    if session[SessionContent.usertype] == "admin":
        return True
    users = PGProcesses.ProcessManagementBase.getAllUsersOfProject(projectID)
    if userID in users:
        return True
    
    return False


#######################################################
def manualCheckIfUserMaySeeProcess(session, userID:str, processID:str) -> bool:
    """
    Look for all users of the process and check if they are allowed to see it

    :param userID: The hashID of the user
    :type userID: str
    :param processID: The processID of the process in question
    :type processID: str
    :return: True if the user belongs to the rightful, false if not
    :rtype: Bool

    """
    if session[SessionContent.usertype] == "admin":
        return True
    users = PGProcesses.ProcessManagementBase.getAllUsersOfProcess(processID)
    if userID in users:
        return True
    
    return False


#################### DECORATOR ###################################
def checkIfUserMaySeeProcess(json=False):
    """
    Check whether a user may see details about this process or not.

    :param json: Controls if the output is in JSON Format or not
    :type json: Bool
    :return: Response whether the user may see the process or not. If so, call the function.
    :rtype: HTTPRespone/JSONResponse, Func
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            userID = profileManagement[request.session[SessionContent.PG_PROFILE_CLASS]].getClientID(request.session)
            if manualCheckIfUserMaySeeProcess(request.session, userID, kwargs["processID"]):
                return func(request, *args, **kwargs)
            else:
                if json:
                    return JsonResponse({}, status=401)
                else:
                    return HttpResponse("Not allowed to see process", status=401)
            
        return inner

    return decorator


#####################################################################
class ExceptionSerializer(serializers.Serializer):
    message = serializers.CharField()
    exception = serializers.CharField()


#################### DECORATOR ###################################
def checkVersion(version=1.0):
    """
    Checks if the version is supported or not. If not, returns an error message.

    :param version: Version of the API to check if it is supported or not
    :type version: Float
    :return: Response whether the version is supported or not
    :rtype: HTTPRespone
    """

    ######################################################
    class VersioningForHandlers(AcceptHeaderVersioning):
        allowed_versions = []

        def __init__(self, allowedVersions) -> None:
            super().__init__()
            self.allowed_versions = [allowedVersions]

    ######################################################
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            versioning = VersioningForHandlers(version)
            version = versioning.determine_version(request)
            if isinstance(version, Exception):
                return Response("Version mismatch!", status=status.HTTP_406_NOT_ACCEPTABLE)
            
        return inner

    return decorator



