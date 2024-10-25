"""
Part of Semper-KI software

Akshay NS 2024

Contains: handlers for events
"""

import logging
from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import serializers
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema


from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, checkVersion
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from code_SemperKI.definitions import *
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.connections.content.postgresql import pgEvents

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#########################################################################
# getMissedEvents
#"getMissedEvents": ("public/getMissedEvents/", events.getMissedEvents)
#########################################################################
#TODO Add serializer for getMissedEvents
#########################################################################
# Handler  
# @extend_schema(
#     summary=" Show how many events (chat messages ...) were missed since last login.",
#     description=" ",
#     tags=['FE - Events'],
#     request=None,
#     responses={
#         200: None,
#         401: ExceptionSerializer,
#         500: ExceptionSerializer
#     }
# )
# @checkIfUserIsLoggedIn(json=True)
# @checkIfRightsAreSufficient(json=True)
# @api_view(["GET"])
# @checkVersion(0.3)
# def getMissedEvents(request:Request):
#     """
#     Show how many events (chat messages ...) were missed since last login.

#     :param request: GET Request
#     :type request: HTTP GET
#     :return: JSON Response with numbers for every process and project
#     :rtype: JSON Response

#     """
#     user = pgProfiles.ProfileManagementBase.getUser(request.session)
#     lastLogin = timezone.make_aware(datetime.strptime(user[UserDescription.lastSeen], '%Y-%m-%d %H:%M:%S.%f+00:00'))
#     projects = pgProcesses.ProcessManagementBase.getProjects(request.session)

#     output = {EventsDescription.eventType: EventsDescription.projectEvent, EventsDescription.events: []}
#     #TODO: organization events like role changed or something
#     for project in projects:
#         currentProject = {}
#         currentProject[ProjectDescription.projectID] = project[ProjectDescription.projectID]
#         processArray = []
#         for process in project[SessionContentSemperKI.processes]:
#             currentProcess = {}
#             currentProcess[ProcessDescription.processID] = process[ProcessDescription.processID]
#             newMessagesCount = 0
#             chat = []
#             for key in process[ProcessDescription.messages]:
#                 chat.extend(process[ProcessDescription.messages][key])  
#             for messages in chat:
#                 if MessageContent.date in messages and lastLogin < timezone.make_aware(datetime.strptime(messages[MessageContent.date], '%Y-%m-%dT%H:%M:%S.%fZ')) and messages[MessageContent.userID] != user[UserDescription.hashedID]:
#                     newMessagesCount += 1
#             if lastLogin < timezone.make_aware(datetime.strptime(process[ProcessDescription.updatedWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')):
#                 processStatusEvent = 1
#             else:
#                 processStatusEvent = 0
            
#             # if something changed, save it. If not, discard
#             if processStatusEvent !=0 or newMessagesCount != 0: 
#                 currentProcess[ProcessDescription.processStatus] = processStatusEvent
#                 currentProcess[ProcessDescription.messages] = newMessagesCount

#                 processArray.append(currentProcess)
#         if len(processArray):
#             currentProject[SessionContentSemperKI.processes] = processArray
#             output[EventsDescription.events].append(currentProject)
    
#     # set accessed time to now
#     pgProfiles.ProfileManagementBase.setLoginTime(user[UserDescription.hashedID])

#     return Response(output, status=status.HTTP_200_OK)


##################################################
#######################################################
class SReqsEventContent(serializers.Serializer):
    events = serializers.ListField(child=serializers.DictField())
    eventType = serializers.CharField(max_length=200)
    triggerEvent = serializers.BooleanField()

#######################################################
class SReqsOneEvent(serializers.Serializer):
    #pgEvents.EventDescription.event, pgEvents.EventDescription.userHashedID, pgEvents.EventDescription.eventID, pgEvents.EventDescription.createdWhen
    eventID = serializers.CharField(max_length=513, required=False)
    userHashedID = serializers.CharField(max_length=513, required=False)
    event = SReqsEventContent()
    createdWhen = serializers.CharField(max_length=200, required=False)

#######################################################
@extend_schema(
    summary="Return all events related to a user",
    description=" ",
    tags=['FE - Events'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SReqsOneEvent()),
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@api_view(["GET"])
@checkVersion(0.3)
def getAllEventsForUser(request:Request):
    """
    Return all events related to a user

    :param request: GET Request
    :type request: HTTP GET
    :return: list of events
    :rtype: Response

    """
    try:
        userHashedID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
        listOfEvents = pgEvents.getAllEventsOfAUser(userHashedID)
        if isinstance(listOfEvents, Exception):
            raise listOfEvents
        outSerializer = SReqsOneEvent(data=listOfEvents, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getAllEventsForUser.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Retrieve one event in particular",
    description=" ",
    tags=['FE - Events'],
    request=None,
    responses={
        200: SReqsOneEvent,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@api_view(["GET"])
@checkVersion(0.3)
def getOneEventOfUser(request:Request, eventID:str):
    """
    Retrieve one event in particular

    :param request: GET Request
    :type request: HTTP GET
    :return: Dict
    :rtype: JSONResponse

    """
    try:
        event = pgEvents.getOneEvent(eventID)
        if isinstance(event, Exception):
            raise event
        outSerializer = SReqsOneEvent(data=event)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getOneEventOfUser.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################
@extend_schema(
    summary="Create an event from the frontend",
    description=" ",
    tags=['FE - Events'],
    request=SReqsOneEvent,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@api_view(["POST"])
@checkVersion(0.3)
def createEvent(request:Request):
    """
    Create an event from the frontend

    :param request: POST Request
    :type request: HTTP POST
    :return: Nothing
    :rtype: Response

    """
    try:
        inSerializer = SReqsOneEvent(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {createEvent.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        event = validatedInput["event"]
        userHashedID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
        retVal = pgEvents.createEventEntry(userHashedID, event)
        if isinstance(retVal, Exception):
            raise retVal
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {createEvent.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#######################################################
@extend_schema(
    summary="Deletes one event",
    description=" ",
    tags=['FE - Events'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@api_view(["DELETE"])
@checkVersion(0.3)
def deleteOneEvent(request:Request, eventID:str):
    """
    Deletes one event

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: Success or not
    :rtype: Response

    """
    try:
        retVal = pgEvents.removeEvent(eventID)
        if isinstance(retVal, Exception):
            raise retVal
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {deleteOneEvent.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#######################################################
@extend_schema(
    summary="Deletes all events of a user",
    description=" ",
    tags=['FE - Events'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@api_view(["DELETE"])
@checkVersion(0.3)
def deleteAllEventsForAUser(request:Request):
    """
    Deletes all events of a user

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: Success or not
    :rtype: Response

    """
    try:
        userHashedID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
        retVal = pgEvents.removeAllEventsForUser(userHashedID)
        if isinstance(retVal, Exception):
            raise retVal
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {deleteAllEventsForAUser.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)