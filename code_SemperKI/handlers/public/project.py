"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Handlers for projects
"""


from http import HTTPMethod
import io, logging
from datetime import datetime

from django.utils import timezone

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities.apiCalls import loginViaAPITokenIfAvailable
from Generic_Backend.code_General.utilities.basics import checkVersion, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.definitions import *
from code_SemperKI.states.states import getFlatStatus
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.logics import projectLogics

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

########################################################
# Get project(s)
#"getFlatProjects": ("public/getFlatProjects/", project.getFlatProjects),
########################################################
# Serializers


########################################################
class SResGetProject(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    projectStatus = serializers.IntegerField()
    client = serializers.CharField(max_length=200)
    projectDetails = serializers.DictField(allow_empty=True)
    createdWhen = serializers.CharField(max_length=200)
    updatedWhen = serializers.CharField(max_length=200)
    accessedWhen = serializers.CharField(max_length=200)
    processes = serializers.ListField(allow_empty=True)

#######################################################
class SResFlatProjectsEntry(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    projectStatus = serializers.IntegerField()
    client = serializers.CharField(max_length=200)
    projectDetails = serializers.DictField(allow_empty=True)
    createdWhen = serializers.CharField(max_length=200)
    updatedWhen = serializers.CharField(max_length=200)
    accessedWhen = serializers.CharField(max_length=200)
    processesCount = serializers.IntegerField()
    processIDs = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    owner = serializers.BooleanField(required=False)
    searchableData = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)

########################################################
class SResGetFlatProjects(serializers.Serializer):
    projects = serializers.ListField(child=SResFlatProjectsEntry(), allow_empty=True)

########################################################
# Handler
#######################################################
@extend_schema(
    summary="Get all projects flattened",
    description=" ",
    request=None,
    tags=['FE - Projects'],
    responses={
        200: SResGetFlatProjects,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    },
)
@api_view([HTTPMethod.GET])
@checkVersion(0.3)
def getFlatProjects(request:Request):
    """
    Retrieve all projects.

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with dict
    :rtype: JSON Response

    """
    try:
        result, statusCode = projectLogics.logicForGetFlatProjects(request)
        if isinstance(result, Exception):
            message = f"Error in getFlatProjects: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        outSerializer = SResGetFlatProjects(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    
    except (Exception) as error:
        message = f"Error in getFlatProjects: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#########################################################################
# getProject
#"getProject": ("public/getProject/<str:projectID>/",project.getProject),
#########################################################################
#TODO Add serializer for getProject
#########################################################################
# Handler  
@extend_schema(
    summary="Get a project by ID",
    description=" ",
    request=None,
    tags=['FE - Projects'],
    responses={
        200: SResGetProject,
        401: ExceptionSerializer,
        404: ExceptionSerializer,
        500: ExceptionSerializer
    },
)
@api_view([HTTPMethod.GET])
@checkVersion(0.3)
def getProject(request, projectID):
    """
    Retrieve project with flat processes.

    :param request: GET Request
    :type request: HTTP GET
    :param projectID: id of the project
    :type projectID: str
    :return: Response with dict
    :rtype: JSON Response

    """
    try:
        result, statusCode = projectLogics.logicForGetProject(request, projectID, getProject.cls.__name__)
        if isinstance(result, Exception):
            message = f"Error in getProject: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        outSerializer = SResGetProject(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    
    except (Exception) as error:
        message = f"Error in getProject: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# TODO serializer
#######################################################
@extend_schema(
    summary="Retrieve all projects for the dashboard",
    description=" ",
    tags=['FE - Projects'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["GET"])
@checkVersion(0.3)
def getProjectForDashboard(request:Request, projectID):
    """
    Retrieve all projects for the dashboard

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response
    :rtype: JSONResponse

    """
    try:
        result, statusCode = projectLogics.logicForGetProjectForDashboard(request, projectID, getProjectForDashboard.cls.__name__)
        if isinstance(result, Exception):
            message = f"Error in {getProjectForDashboard.cls.__name__}: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(result, status=statusCode)
    except (Exception) as error:
        message = f"Error in {getProjectForDashboard.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#########################################################################
# Create project
#"createProjectID": ('public/createProjectID/', project.createProjectID),
#######################################################
# Serializers     
        
#######################################################
class SReqCreateProjectID(serializers.Serializer):
    title = serializers.CharField(max_length=200)
        
#######################################################
class SResCreateProjectID(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)

#######################################################
# Handler
@extend_schema(
    summary="Create project and send ID back to frontend",
    description=" ",
    request=SReqCreateProjectID,
    tags=['FE - Projects'],
    responses={
        200: SResCreateProjectID,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    },
)
@loginViaAPITokenIfAvailable()
@api_view([HTTPMethod.POST])
@checkVersion(0.3)
def createProjectID(request:Request):
    """
    Create project and send ID to frontend

    :param request: POST Request
    :type request: HTTP POST
    :return: project ID as string
    :rtype: JSONResponse

    """
    try:
        inSerializer = SReqCreateProjectID(data=request.data)
        if not inSerializer.is_valid():
            message = "Verification failed in createProjectID"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        result, statusCode = projectLogics.logicForCreateProjectID(request, validatedInput, createProjectID.cls.__name__)
        if isinstance(result, Exception):
            message = f"Error in createProjectID: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        outSerializer = SResCreateProjectID(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in createProjectID: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#########################################################################
########################################################
# Update project
#"updateProject": ("public/updateProject/" ,project.updateProject),
########################################################
# Serializers
#######################################################
class SReqUpdateProjectChanges(serializers.Serializer):
    projectStatus = serializers.IntegerField(required=False)
    projectDetails = serializers.DictField(required=False)

##################################################
class SReqUpdateProject(serializers.Serializer):
    projectID = serializers.CharField(max_length=513)
    changes = SReqUpdateProjectChanges()

########################################################
# Handler
@extend_schema(
    summary="Update stuff about the project",
    description=" ",
    request=SReqUpdateProject,
    tags=['FE - Projects'],
    responses={
        200: None,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    },
)
@api_view([HTTPMethod.PATCH])
@checkVersion(0.3)
def updateProject(request:Request):
    """
    Update stuff about the project

    :param request: Request with content
    :type request: HTTP PATCH
    :return: Message if it worked or not
    :rtype: HTTPResponse

    """
    try:
        inSerializer = SReqUpdateProject(data=request.data)
        if not inSerializer.is_valid():
            message = "Validation failed"
            exception = inSerializer.errors
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        validatedInput = inSerializer.data
        result, statusCode = projectLogics.logicForUpdateProject(request, validatedInput, updateProject.cls.__name__)
        if isinstance(result, Exception):
            message = f"Error in updateProject: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response("Success")
            
    except (Exception) as error:
        message = f"Error in updateProject: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

########################################################
# Delete projects
#"deleteProjects": ("public/deleteProjects/" ,project.deleteProjects),
########################################################
# Serializers

########################################################
# Handler
@extend_schema(
    summary="Delete the whole projects",
    description=" ",
    request=None,
    tags=['FE - Projects'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    },
    parameters=[OpenApiParameter(
        name='projectIDs',
        type={'type': 'array', 'minItems': 1, 'items': {'type': 'string'}},
        location=OpenApiParameter.QUERY,
        required=True,
        style='form',
        explode=False,
    )],
)
@api_view([HTTPMethod.DELETE])
@checkVersion(0.3)
def deleteProjects(request:Request):
    """
    Delete whole projects

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: Success or not
    :rtype: HTTPResponse

    """
    try:
        result, statusCode = projectLogics.logicForDeleteProjects(request, deleteProjects.cls.__name__)
        if isinstance(result, Exception):
            message = f"Error in deleteProjects: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response("Success", status=status.HTTP_200_OK)
    
    except (Exception) as error:
        message = f"Error in deleteProjects: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#########################################################################
# saveProjects
#"deleteProjects": ("public/deleteProjects/" ,project.deleteProjects),
#########################################################################
#TODO Add serializer for saveProjects
#########################################################################
# Handler  
@extend_schema(
    summary="Save projects to database",
    description=" ",
    tags=['FE - Projects'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
# @checkIfUserIsLoggedIn()
# @checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
def saveProjects(request:Request):
    """
    Save projects to database

    :param request: GET Request
    :type request: HTTP GET
    :return: Response if sent successfully or not
    :rtype: HTTP Response

    """
    try:
        result = projectLogics.logicForSaveProjects(request.session)
        if isinstance(result, Exception):
            raise result
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in saveProjects: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
###################################################
def saveProjectsViaWebsocket(session):
    """
    Save projects to database

    :param session: session of user
    :type session: Dict
    :return: None
    :rtype: None

    """
    try:
        result = projectLogics.logicForSaveProjects(session)
        if isinstance(result, Exception):
            raise result
        return None
    
    except (Exception) as error:
        loggerError.error(f"saveProjectsViaWebsocket: {str(error)}")
        return error        