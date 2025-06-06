"""
Part of Semper-KI software

Akshay NS 2024

Contains: State machine handlers
"""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import serializers
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkVersion

from code_SemperKI.definitions import *
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.states.states import StateMachine, InterfaceForStateChange
from code_SemperKI.logics.statemachineLogics import logicForStatusButtonRequest

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#########################################################################
# getStateMachine
#"getStateMachine": ("private/getStateMachine/", statemachine.getStateMachine)
#########################################################################
#TODO Add serializer for getStateMachine
#########################################################################
# Handler  
@extend_schema(
    summary="Print out the whole state machine and all transitions",
    description=" ",
    request=None,
    tags = ['BE - State machine'],
    responses={
        200: None,
        500: ExceptionSerializer
    }
)
@api_view(["GET"])
@checkVersion(0.3)
def getStateMachine(request:Request):
    """
    Print out the whole state machine and all transitions

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with graph in JSON Format
    :rtype: JSONResponse
    
    """
    try:
        sm = StateMachine(initialAsInt=0)
        paths = sm.showPaths()
        return Response(paths, status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in getStateMachine: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#########################################################################
# statusButtonRequest
#"statusButtonRequest": ("public/statusButtonRequest/", miscellaneous.statusButtonRequest)
#########################################################################
# Serializers
#######################################################
class SReqButtonData(serializers.Serializer):
    type = serializers.CharField(max_length=200)
    targetStatus = serializers.CharField(max_length=200, required=False)
#######################################################
class SReqStatusButtons(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    processIDs = serializers.ListField(child=serializers.CharField(max_length=200))
    buttonData = SReqButtonData()
#########################################################################
# Handler   
@extend_schema(
    summary="Button was clicked, so the state must change (transition inside state machine)",
    description=" ",
    tags=['FE - State machine'],
    request=SReqStatusButtons,
    responses={
        200: None,
        400: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["POST"])
@checkVersion(0.3)
def statusButtonRequest(request:Request):
    """
    Button was clicked, so the state must change (transition inside state machine)
    
    :param request: POST Request
    :type request: HTTP POST
    :return: Response with new buttons
    :rtype: JSONResponse
    """
    try:
        # get from info, create correct object, initialize statemachine, switch state accordingly
        inSerializer = SReqStatusButtons(data=request.data)
        if not inSerializer.is_valid():
            message = "Verification failed in statusButtonRequest"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        info = inSerializer.data

        return logicForStatusButtonRequest(request, info, statusButtonRequest.cls.__name__)
        
    except (Exception) as error:
        message = f"Error in statusButtonRequest: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################