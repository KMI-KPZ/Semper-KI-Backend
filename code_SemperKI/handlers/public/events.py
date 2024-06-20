"""
Part of Semper-KI software

Akshay NS 2024

Contains: handlers for events
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
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.connections.content.postgresql import pgProcesses

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

# "getMissedEvents": ("public/getMissedEvents/", miscellaneous.getMissedEvents),
#######################################################
@extend_schema(
    summary=" Show how many events (chat messages ...) were missed since last login.",
    description=" ",
    tags=['miscellaneous'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn(json=True)
@checkIfRightsAreSufficient(json=True)
@api_view(["GET"])
def getMissedEvents(request):
    """
    Show how many events (chat messages ...) were missed since last login.

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response with numbers for every process and project
    :rtype: JSON Response

    """
    user = pgProfiles.ProfileManagementBase.getUser(request.session)
    lastLogin = timezone.make_aware(datetime.strptime(user[UserDescription.lastSeen], '%Y-%m-%d %H:%M:%S.%f+00:00'))
    projects = pgProcesses.ProcessManagementBase.getProjects(request.session)

    output = {EventsDescription.eventType: EventsDescription.projectEvent, EventsDescription.events: []}
    #TODO: organization events like role changed or something
    for project in projects:
        currentProject = {}
        currentProject[ProjectDescription.projectID] = project[ProjectDescription.projectID]
        processArray = []
        for process in project[SessionContentSemperKI.processes]:
            currentProcess = {}
            currentProcess[ProcessDescription.processID] = process[ProcessDescription.processID]
            newMessagesCount = 0
            chat = process[ProcessDescription.messages]["messages"]
            for messages in chat:
                if MessageContent.date in messages and lastLogin < timezone.make_aware(datetime.strptime(messages[MessageContent.date], '%Y-%m-%dT%H:%M:%S.%fZ')) and messages[MessageContent.userID] != user[UserDescription.hashedID]:
                    newMessagesCount += 1
            if lastLogin < timezone.make_aware(datetime.strptime(process[ProcessDescription.updatedWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')):
                status = 1
            else:
                status = 0
            
            # if something changed, save it. If not, discard
            if status !=0 or newMessagesCount != 0: 
                currentProcess[ProcessDescription.processStatus] = status
                currentProcess[ProcessDescription.messages] = newMessagesCount

                processArray.append(currentProcess)
        if len(processArray):
            currentProject[SessionContentSemperKI.processes] = processArray
            output[EventsDescription.events].append(currentProject)
    
    # set accessed time to now
    pgProfiles.ProfileManagementBase.setLoginTime(user[UserDescription.hashedID])

    return JsonResponse(output, status=200, safe=False)