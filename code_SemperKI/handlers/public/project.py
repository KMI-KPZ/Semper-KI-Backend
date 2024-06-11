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
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities.basics import manualCheckIfRightsAreSufficient, manualCheckifLoggedIn
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.definitions import *
from code_SemperKI.states.states import getFlatStatus
from code_SemperKI.utilities.basics import ExceptionSerializer, checkVersion

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

#########################################################################
########################################################
# Get project(s)
########################################################
# Serializers

########################################################
class ProjectDetailsSerializer(serializers.Serializer):
    title = serializers.CharField()

########################################################
class SResGetProject(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    projectStatus = serializers.IntegerField()
    client = serializers.CharField(max_length=200)
    projectDetails = ProjectDetailsSerializer()
    createdWhen = serializers.CharField(max_length=200)
    updatedWhen = serializers.CharField(max_length=200)
    accessedWhen = serializers.CharField(max_length=200)
    processes = serializers.ListField()
########################################################
class SResGetFlatProjects(serializers.Serializer):
    projects = serializers.ListField()#TODO specify further

########################################################
# Handler
#######################################################
@extend_schema(
    summary="Get all projects flattened",
    description=" ",
    request=None,
    responses={
        200: SResGetFlatProjects,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    },
)
@api_view([HTTPMethod.GET])
@checkVersion(0.3)
def getFlatProjects(request):
    """
    Retrieve all projects.

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with dict
    :rtype: JSON Response

    """
    try:
        outDict = {"projects": []}
        contentManager = ManageContent(request.session)

        # Gather from session...
        if contentManager.sessionManagement.getIfContentIsInSession():
            sessionContent = contentManager.sessionManagement.getProjectsFlat(request.session)
            outDict["projects"].extend(sessionContent)
        
        # ... and from database
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, getFlatProjects.cls.__name__):           
            objFromDB = contentManager.postgresManagement.getProjectsFlat(request.session)
            if len(objFromDB) >= 1:
                outDict["projects"].extend(objFromDB)

        outDict["projects"] = sorted(outDict["projects"], key=lambda x: 
                timezone.make_aware(datetime.strptime(x[ProjectDescription.createdWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
        
        outSerializer = SResGetFlatProjects(data=outDict)
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


#######################################################
@checkVersion(0.3)
@extend_schema(
    summary="Get a project by ID",
    description=" ",
    request=None,
    responses={
        200: SResGetProject,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    },
)
@api_view([HTTPMethod.GET])
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
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(getProject.cls.__name__)
        if interface == None:
            message = "Rights not sufficient in getProject"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        projectAsDict = interface.getProject(projectID)
        processList = projectAsDict[SessionContentSemperKI.processes]
        listOfFlatProcesses = []
        for entry in processList:
            flatProcessDict = {
                ProcessDetails.title: entry[ProcessDescription.processDetails][ProcessDetails.title] if ProcessDetails.title in entry[ProcessDescription.processDetails] else entry[ProcessDescription.processID],
                ProcessDescription.processID: entry[ProcessDescription.processID],
                ProcessDescription.serviceType: entry[ProcessDescription.serviceType],
                ProcessDescription.updatedWhen: entry[ProcessDescription.updatedWhen],
                ProcessDescription.createdWhen: entry[ProcessDescription.createdWhen],
                "flatProcessStatus": getFlatStatus(entry[ProcessDescription.processStatus], contentManager.getClient() == entry[ProcessDescription.client]),
                ProcessDetails.amount: entry[ProcessDescription.processDetails][ProcessDetails.amount] if ProcessDetails.amount in entry[ProcessDescription.processDetails] else 1,
                ProcessDetails.imagePath: entry[ProcessDescription.processDetails][ProcessDetails.imagePath] if ProcessDetails.imagePath in entry[ProcessDescription.processDetails] else ""
            }
            listOfFlatProcesses.append(flatProcessDict)

        projectAsDict[SessionContentSemperKI.processes] = listOfFlatProcesses

        outSerializer = SResGetProject(data=projectAsDict)
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

#########################################################################
# Create project
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
@checkVersion(0.3)
@extend_schema(
    summary="Create project and send ID back to frontend",
    description=" ",
    request=SReqCreateProjectID,
    responses={
        200: SResCreateProjectID,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    },
)
@api_view([HTTPMethod.POST])
def createProjectID(request):
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
            exception = "Verification failed"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        projectTitle = validatedInput[ProjectDetails.title]

        # generate ID string, make timestamp and create template for project
        projectID = crypto.generateURLFriendlyRandomString()
        #now = timezone.now()
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(createProjectID.cls.__name__)
        if interface == None:
            message = "Rights not sufficient in createProjectID"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
        client = contentManager.getClient()
        interface.createProject(projectID, client)
        interface.updateProject(projectID, ProjectUpdates.projectDetails, {ProjectDetails.title: projectTitle})

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))

        #return just the id for the frontend
        output = {ProjectDescription.projectID: projectID}
        outSerializer = SResCreateProjectID(data=output)
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
########################################################
# Serializers
class SReqUpdateProject(serializers.Serializer):
    projectID = serializers.CharField(required=True, max_length=100)
    changes = serializers.JSONField(required=True)

########################################################
# Handler
@checkVersion(0.3)
@extend_schema(
    summary="Update stuff about the project",
    description=" ",
    request=SReqUpdateProject,
    responses={
        200: None,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    },
)
@api_view([HTTPMethod.PATCH])
def updateProject(request):
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
            exception = "Validation failed"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        validatedInput = inSerializer.data
        projectID = validatedInput[ProjectDescription.projectID]

        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(updateProject.cls.__name__)
        if interface == None or not contentManager.checkRightsForProject(projectID):
            message = "Rights not sufficient in updateProject"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        for entry in validatedInput["changes"]:
            returnVal = interface.updateProject(projectID, entry, validatedInput["changes"][entry])
            if isinstance(returnVal, Exception):
                raise returnVal
            
        # TODO send to websockets that are active, that a new message/status is available for that project
        # outputDict = {EventsDescription.eventType: "projectEvent"}
        # outputDict["projectID"] = projectID
        # outputDict["projects"] = [{"projectID": projectID, "status": 1, "messages": 0}]
        # channel_layer = get_channel_layer()
        # listOfUsers = pgProcesses.ProcessManagementBase.getAllUsersOfProject(projectID)
        # for user in listOfUsers:
        #     if user.subID != pgProfiles.ProfileManagementBase.getUserKey(session=request.session):
        #         async_to_sync(channel_layer.group_send)(pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=user.subID), {
        #             "type": "sendMessageJSON",
        #             "dict": outputDict,
        #         })
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.EDITED},updated,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))

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

#########################################################################
########################################################
# Delete projects
########################################################
# Serializers

########################################################
# Handler
@checkVersion(0.3)
@extend_schema(
    summary="Delete the whole projects",
    description=" ",
    request=None,
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
def deleteProjects(request):
    """
    Delete whole projects

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: Success or not
    :rtype: HTTPResponse

    """
    try:
        projectIDs = request.data['projectIDs']
        #loggedIn = False # don't check rights in every iteration

        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(deleteProjects.cls.__name__)
        if interface == None:
            message = "Rights not sufficient in updateProject"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        for projectID in projectIDs:
            if not contentManager.checkRightsForProject(projectID):
                message = "Rights not sufficient in updateProject"
                exception = "Unauthorized"
                logger.error(message)
                exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
                if exceptionSerializer.is_valid():
                    return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            interface.deleteProject(projectID)
            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))
        
        return Response("Success")
    
    except (Exception) as error:
        message = f"Error in deleteProjects: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

