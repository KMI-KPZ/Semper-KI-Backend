"""
Part of Semper-KI software

Akshay NS 2024

Contains: Handlers for admin views (similar to the handlers/admin.py file. If needed, the other file can be deleted)
"""
import json, logging, copy
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities import basics
from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.connections.content.postgresql import pgProcesses

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#########Serializer#############
#TODO Add serializer  
# "getAllProjectsFlatAsAdmin": ("public/getAllProjectsFlatAsAdmin/", admin_.getAllProjectsFlatAsAdmin),
#######################################################
@extend_schema(
    summary="Get all Projects in flat format.",
    description=" ",
    tags=['admin'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@basics.checkIfUserIsLoggedIn(json=True)
@basics.checkIfUserIsAdmin(json=True)
@api_view(["GET"])
def getAllProjectsFlatAsAdmin(request):
    """
    Get all Projects in flat format.

    :param request: GET request
    :type request: HTTP GET
    :return: JSON response
    :rtype: JSONResponse
    """
    try:
        # get all projects if you're an admin
        projects = pgProcesses.ProcessManagementBase.getAllProjectsFlat()
        for idx, entry in enumerate(projects):
            clientID = entry[ProcessDescription.client]
            userName = pgProfiles.ProfileManagementBase.getUserNameViaHash(clientID)
            projects[idx]["clientName"] = userName
        
        logger.info(f"{Logging.Subject.ADMIN},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},fetched,{Logging.Object.SYSTEM},all projects," + str(datetime.datetime.now()))
        return JsonResponse(projects, safe=False)
    except (Exception) as error:
        message = f"Error in getAllProjectsFlatAsAdmin: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#########Serializer#############
#TODO Add serializer  
# "getSpecificProjectAsAdmin": ("public/getSpecificProjectAsAdmin/", admin_.getSpecificProjectAsAdmin),
#######################################################
@extend_schema(
    summary="Get all info for a specific project.",
    description=" ",
    tags=['admin'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@basics.checkIfUserIsLoggedIn(json=True)
@basics.checkIfUserIsAdmin(json=True)
@api_view(["GET"])
def getSpecificProjectAsAdmin(request, projectID):
    """
    Get all info for a specific project.

    :param request: GET request
    :type request: HTTP GET
    :param projectID: Project for which details are necessary
    :type projectID: str
    :return: JSON response
    :rtype: JSONResponse
    """
    try:
        logger.info(f"{Logging.Subject.ADMIN},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},fetched,{Logging.Object.SYSTEM},project {projectID}," + str(datetime.datetime.now()))
        return JsonResponse(pgProcesses.ProcessManagementBase.getProject(projectID))
    except (Exception) as error:
        message = f"Error in getSpecificProjectAsAdmin: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        