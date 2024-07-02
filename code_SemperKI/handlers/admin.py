"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling of admin view requests

"""

import datetime, logging

from django.http import  JsonResponse

from Generic_Backend.code_General.utilities import basics
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from code_SemperKI.utilities.serializer import ExceptionSerializer
from ..connections.content.postgresql import pgProcesses
from ..definitions import ProcessDescription

logger = logging.getLogger("logToFile")

# Projects #############################################################################################################

##############################################
#########Serializer#############
#TODO Add serializer  
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
    # get all projects if you're an admin
    projects = pgProcesses.ProcessManagementBase.getAllProjectsFlat()
    for idx, entry in enumerate(projects):
        clientID = entry[ProcessDescription.client]
        userName = pgProfiles.ProfileManagementBase.getUserNameViaHash(clientID)
        projects[idx]["clientName"] = userName
        
    logger.info(f"{basics.Logging.Subject.ADMIN},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{basics.Logging.Predicate.FETCHED},fetched,{basics.Logging.Object.SYSTEM},all projects," + str(datetime.datetime.now()))
    return Response(projects, safe=False)

##############################################
#########Serializer#############
#TODO Add serializer  
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

    logger.info(f"{basics.Logging.Subject.ADMIN},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{basics.Logging.Predicate.FETCHED},fetched,{basics.Logging.Object.SYSTEM},project {projectID}," + str(datetime.datetime.now()))
    return JsonResponse(pgProcesses.ProcessManagementBase.getProject(projectID))

    