"""
Part of Semper-KI software

Akshay NS 2024, Silvio Weging 2025

Contains: Logics for state machine handlers
"""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request

from Generic_Backend.code_General.definitions import *

from code_SemperKI.definitions import *
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.handlers.public.process import logicForCloneProcesses, deleteProcessFunction
from code_SemperKI.states.states import StateMachine, InterfaceForStateChange

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
def logicForStatusButtonRequest(request:Request, validatedInput:dict, functionName:str):
    """
    Logic for status button request

    :param request: Request
    :type request: Request
    :param validatedInput: Validated input
    :type validatedInput: dict
    :param functionName: Function name
    :type functionName: str
    :return: Response|Exception, status code
    :rtype: Response|Exception, int
    
    """
    try:
        projectID = validatedInput[InterfaceForStateChange.projectID]
        processIDs = validatedInput[InterfaceForStateChange.processIDs]
        buttonData = validatedInput[InterfaceForStateChange.buttonData]
        if "deleteProcess" in buttonData[InterfaceForStateChange.type]:
            retVal = deleteProcessFunction(request.session, processIDs, projectID)
            if isinstance(retVal, Exception):
                raise retVal
            return retVal
        elif "cloneProcess" in buttonData[InterfaceForStateChange.type]:
            retVal, statusCode = logicForCloneProcesses(request, projectID, processIDs, "cloneProcesses")
            if isinstance(retVal, Exception):
                message = f"Error in {functionName}: {str(retVal)}"
                exception = str(retVal)
                loggerError.error(message)
                exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
                if exceptionSerializer.is_valid():
                    return Response(exceptionSerializer.data, status=statusCode)
                else:
                    return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(retVal, status=statusCode)
        else:
            if InterfaceForStateChange.targetStatus not in buttonData:
                raise Exception("Target status not provided")
            nextState = buttonData[InterfaceForStateChange.targetStatus]

            contentManager = ManageContent(request.session)
            interface = contentManager.getCorrectInterface(functionName)
            for processID in processIDs:
                process = interface.getProcessObj(projectID, processID)
                sm = StateMachine(initialAsInt=process.processStatus)
                sm.onButtonEvent(nextState, interface, process)
        
            return Response({}, status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {functionName}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)