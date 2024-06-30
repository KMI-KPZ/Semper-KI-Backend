"""
Part of Semper-KI software

Akshay NS 2024

Contains: Handlers for miscellaneous [services, statusbuttons]
"""

import logging
from django.http import JsonResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.handlers.public.process import cloneProcess, deleteProcessFunction
from code_SemperKI.states.states import StateMachine, InterfaceForStateChange


logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
loggerDebug = logging.getLogger("django_debug")
##################################################

#########################################################################
# getServices
#########################################################################
#TODO Add serializer for getServices
#########################################################################
# Handler    
@extend_schema(
    summary="Return the offered services",
    description=" ",
    request=None,
    tags = ['miscellaneous'],
    responses={
        200: None,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
def getServices(request):
    """
    Return the offered services
downloadFileStream), #
    :param request: The request object
    :type request: Dict
    :return: The Services as dictionary with string and integer coding
    :rtype: JSONResponse
    
    """
    try:
        output = serviceManager.getAllServices()
        return Response(output, status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in getServices: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#########################################################################
# statusButtonRequest
#########################################################################
#TODO Add serializer for statusButtonRequest
#########################################################################
# Handler   
@extend_schema(
    summary="Button was clicked, so the state must change (transition inside state machine)",
    description=" ",
    tags=['public'],
    request=None,
    responses={
        200: None,
        500: ExceptionSerializer
    }
)
@api_view(["GET"])
def statusButtonRequest(request):
    """
    Button was clicked, so the state must change (transition inside state machine)
    
    :param request: POST Request
    :type request: HTTP POST
    :return: Response with new buttons
    :rtype: JSONResponse
    """
    try:
        # get from info, create correct object, initialize statemachine, switch state accordingly
        info = json.loads(request.body.decode("utf-8"))
        projectID = info[InterfaceForStateChange.projectID]
        processIDs = info[InterfaceForStateChange.processIDs]
        buttonData = info[InterfaceForStateChange.buttonData]
        if "deleteProcess" in buttonData[InterfaceForStateChange.type]:
            retVal = deleteProcessFunction(request.session, processIDs)
            if isinstance(retVal, Exception):
                raise retVal
            return retVal
        elif "cloneProcess" in buttonData[InterfaceForStateChange.type]:
            retVal = cloneProcess(request, projectID, processIDs)
            if isinstance(retVal, Exception):
                raise retVal
            return retVal
        else:
            nextState = buttonData[InterfaceForStateChange.targetStatus]

            contentManager = ManageContent(request.session)
            interface = contentManager.getCorrectInterface(statusButtonRequest.cls.__name__)
            for processID in processIDs:
                process = interface.getProcessObj(projectID, processID)
                sm = StateMachine(initialAsInt=process.processStatus)
                sm.onButtonEvent(nextState, interface, process)

        return JsonResponse({})
    except (Exception) as error:
        message = f"Error in statusButtonRequest: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
##############################################