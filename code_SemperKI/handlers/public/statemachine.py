"""
Part of Semper-KI software

Akshay NS 2024

Contains: 
"""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema


from Generic_Backend.code_General.definitions import *

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.states.states import StateMachine

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#########Serializer#############
#TODO Add serializer  
#######################################################
@extend_schema(
    summary="Print out the whole state machine and all transitions",
    description=" ",
    request=None,
    tags = ['state machine'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["GET"])
def getStateMachine(request):
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
        
#######################################