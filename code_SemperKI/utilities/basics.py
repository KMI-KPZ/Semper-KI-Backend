"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Basic stuff like decorators and such that is imported in Semper KI
"""

import json

from functools import wraps
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from rest_framework import exceptions
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
# class ExceptionSerializer(serializers.Serializer):
#     message = serializers.CharField()
#     exception = serializers.CharField()




#################### DECORATOR ###################################
class VersioningForHandlers(AcceptHeaderVersioning):
    allowed_versions = ["0.3"] # default for swagger

    def __init__(self, allowedVersions) -> None:
        super().__init__()
        if str(allowedVersions) not in self.allowed_versions:
            self.allowed_versions = [str(allowedVersions)]
######################################################
def checkVersion(version=0.3):
    """
    Checks if the version is supported or not. If not, returns an error message.

    :param version: Version of the API to check if it is supported or not
    :type version: Float
    :return: Response whether the version is supported or not
    :rtype: HTTPRespone
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            try:
                if request.version == None:
                    #getting really tired of swaggers bullshit (of sometimes not sending the correct header)
                    return func(request, *args, **kwargs)
                versioning = VersioningForHandlers(version)
                versionOfReq = versioning.determine_version(request)
                return func(request, *args, **kwargs)
            except exceptions.NotAcceptable as e:
                return HttpResponse(f"Version mismatch! {version} required!", status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                return HttpResponse(f"Exception in {func.__name__}: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return inner

    return decorator

#######################################################
class StaticMediaContentForSemperKI:
    """
    Class that holds all static media content for Semper-KI
    """

    #######################################################
    def __init__(self):
        with open(str(settings.BASE_DIR) + "/code_SemperKI/mediaConfig.json") as configFile:
            config = json.load(configFile)
            self.config = config

    #######################################################
    # Static Media Content
    def getValue(self, key:str) -> str:
        """
        Retrieve value from config file

        :param key: Key to retrieve value for
        :type key: str
        :return: Value for the key
        :rtype: str

        """
        if key in self.config:
            return settings.STATIC_URL + self.config[key]
        else:
            return ""
staticMediaContentForSemperKI = StaticMediaContentForSemperKI()

#######################################################
testPicture = staticMediaContentForSemperKI.getValue("testpicture")
previewNotAvailable = staticMediaContentForSemperKI.getValue("previewNotAvailable")
previewNotAvailableGER = staticMediaContentForSemperKI.getValue("previewNotAvailableGER")
kissLogo = staticMediaContentForSemperKI.getValue("kissLogo")
