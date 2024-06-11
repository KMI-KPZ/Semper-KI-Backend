"""
Part of Semper-KI software

Akshay NS 2024

Contains: Handlers for processes
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
from Generic_Backend.code_General.utilities.basics import manualCheckifAdmin
from Generic_Backend.code_General.utilities import crypto, rights
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from code_SemperKI.states.states import processStatusAsInt, ProcessStatusAsString, StateMachine, getButtonsForProcess

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.utilities.basics import ExceptionSerializer
from code_SemperKI.handlers.public.project import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################


# "createProcessID": ("public/createProcessID/", process.createProcessID),
####################################################
#########Serializer#############
class SResCreateProcessID(serializers.Serializer):
    processID = serializers.CharField(max_length=200)

#######################################################
@extend_schema(
    summary="Create a process ID ",
    description="creates a process ID for a given project id",
    request=None,
    responses={
        200: SResCreateProcessID,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
# @checkIfUserIsLoggedIn()
# @require_http_methods(["GET"])
# @checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
def createProcessID(request, projectID):
    """
    Create process ID for frontend

    :param request: GET Request
    :type request: HTTP GET
    :param projectID: id of the project the created process should belong to
    :type projectID: str
    :return: process ID as string
    :rtype: JSONResponse

    """
    try:
        # generate ID, timestamp and template for process
        processID = crypto.generateURLFriendlyRandomString()
        
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(createProcessID.__name__)
        if interface == None:
            message = "Rights not sufficient in createProcessID"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        client = contentManager.getClient()
        interface.createProcess(projectID, processID, client)

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

        #return just the id for the frontend
        output = {ProcessDescription.processID: processID}
        outSerializer = SResCreateProcessID(data=output)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in createProcessID: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# "getProcess": ("public/getProcess/", process.getProcess),
##############################
###serializer###########
class SResGetProcess(serializers.Serializer):
    process = serializers.ListField()
#######################################################
@extend_schema(
    summary="Retrieve complete process.",
    description="Retrieve complete process using projectID and processID ",
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
# @checkIfUserIsLoggedIn()
# @require_http_methods(["GET"])
# @checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
def getProcess(request, projectID, processID):
    """
    Retrieve complete process.

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with list
    :rtype: JSON Response

    """
    try:
        contentManager = ManageContent(request.session)
        userID = contentManager.getClient()
        adminOrNot = manualCheckifAdmin(request.session)
        interface = contentManager.getCorrectInterface(getProject.cls.__name__)
        if interface == None:
            message = "Rights not sufficient in getProcess"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        process = interface.getProcess(projectID, processID)
        if process != {}:
            buttons = getButtonsForProcess(process[ProcessDescription.processStatus], process[ProcessDescription.client] == userID, adminOrNot) # calls current node of the state machine
            process["processStatusButtons"] = buttons
        #return just list of process.
        outSerializer = SResGetProcess(data=process)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)    
            
        
    except (Exception) as error:
        message = f"Error in getProcess: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        