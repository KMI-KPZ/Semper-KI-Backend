import io, logging
from datetime import datetime

from django.utils import timezone

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities.basics import manualCheckIfRightsAreSufficient, manualCheckifLoggedIn
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.definitions import *
from code_SemperKI.states.states import getFlatStatus
from code_SemperKI.utilities.basics import ExceptionSerializer

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
class ProjectInterface(APIView):
    """
    Interface for handling project related requests.
    
    """
#########################################################################
    ########################################################
    # Get project(s)
    ########################################################
    # Serializers
    class SResGetProject(serializers.Serializer):
        projectID = serializers.CharField(max_length=200)
        projectStatus = serializers.IntegerField()
        client = serializers.CharField(max_length=200)
        projectDetails = serializers.JSONField()
        createdWhen = serializers.CharField(max_length=200)
        updatedWhen = serializers.CharField(max_length=200)
        accessedWhen = serializers.CharField(max_length=200)
        processes = serializers.ListField()
    ########################################################
    class SResGetFlatProjects(serializers.Serializer):
        projects = serializers.ListField()

    ########################################################
    # Handler
    #######################################################
    def getFlatProjects(self, request):
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
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, self.getProcess.__name__):           
                objFromDB = contentManager.postgresManagement.getProjectsFlat(request.session)
                if len(objFromDB) >= 1:
                    outDict["projects"].extend(objFromDB)

            outDict["projects"] = sorted(outDict["projects"], key=lambda x: 
                    timezone.make_aware(datetime.strptime(x[ProjectDescription.createdWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            
            outSerializer = self.SResGetFlatProjects(data=outDict)
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        
        except (Exception) as error:
            message = f"Error in getFlatProjects: {str(error)}"
            exception = str(error)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    #######################################################
    def getProject(self, request, projectID):
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
            interface = contentManager.getCorrectInterface(self.getProject.__name__)
            if interface == None:
                message = "Rights not sufficient in getProject"
                exception = "Unauthorized"
                logger.error(message)
                exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            
            
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

            outSerializer = self.SResGetProject(data=projectAsDict)
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        
        except (Exception) as error:
            message = f"Error in getProject: {str(error)}"
            exception = str(error)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #######################################################
    # Interface
    @extend_schema(
        summary="Get a project by ID",
        request=None,
        responses={
            200: SResGetProject,
            401: ExceptionSerializer,
            500: ExceptionSerializer
        },
    )
    def getHandlerForProject(self, request, projectID):
        return self.getProject(request, projectID)
    #######################################################
    @extend_schema(
        summary="Get all projects flattened",
        request=None,
        responses={
            200: SResGetFlatProjects,
            401: ExceptionSerializer,
            500: ExceptionSerializer
        },
    )
    @api_view(['GET'])
    def getHandlerForFlatProjects(self, request):
        return self.getFlatProjects(request)

    #######################################################
    def dispatch(self, request, *args, **kwargs):
        """
        Overwrite the default dispatch method to handle GET requests for projectID
        """
        if request.method.lower() == "get":
            if request.GET.get('projectID'):
                return self.getHandlerForProject(request, *args)
            else:
                return self.getHandlerForFlatProjects(request)
        else:
            return super().dispatch(request, *args, **kwargs)

#########################################################################
    # Create project
    #######################################################
    # Serializers     
    class SResCreateProjectID(serializers.Serializer):
        projectID = serializers.CharField(max_length=200)

    #######################################################
    # Handler
    def createProjectID(self, request):
        """
        Create project and send ID to frontend

        :param request: POST Request
        :type request: HTTP POST
        :return: project ID as string
        :rtype: JSONResponse

        """
        try:
            # generate ID string, make timestamp and create template for project
            projectID = crypto.generateURLFriendlyRandomString()
            #now = timezone.now()
            contentManager = ManageContent(request.session)
            interface = contentManager.getCorrectInterface(self.createProjectID.__name__)
            if interface == None:
                message = "Rights not sufficient in createProjectID"
                exception = "Unauthorized"
                logger.error(message)
                exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            
            client = contentManager.getClient()
            interface.createProject(projectID, client)

            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))

            #return just the id for the frontend
            output = {ProjectDescription.projectID: projectID}
            outSerializer = self.SResCreateProjectID(data=output)
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        except (Exception) as error:
            message = f"Error in createProjectID: {str(error)}"
            exception = str(error)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    #######################################################
    # Interface
    @extend_schema(
        summary="Create project and send ID back to frontend",
        request=None,
        responses={
            200: SResCreateProjectID,
            401: ExceptionSerializer
        },
    )
    def post(self, request):
        return self.createProjectID(request)
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
    def updateProject(self, request):
        """
        Update stuff about the project

        :param request: Request with content
        :type request: HTTP PATCH
        :return: Message if it worked or not
        :rtype: HTTPResponse

        """
        try:
            json_data=request.body
            stream= io.BytesIO(json_data)
            jsonContent = JSONParser().parse(stream)
            serializer = self.SReqUpdateProject(data=jsonContent)
            if serializer.is_valid():
                validatedInput = serializer.data
                projectID = validatedInput[ProjectDescription.projectID]

                contentManager = ManageContent(request.session)
                interface = contentManager.getCorrectInterface(self.updateProject.__name__)
                if interface == None or not contentManager.checkRightsForProject(projectID):
                    message = "Rights not sufficient in updateProject"
                    exception = "Unauthorized"
                    logger.error(message)
                    exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
                    return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)

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
            else:
                message = "Validation failed"
                exception = "Validation failed"
                logger.error(message)
                exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)

        except (Exception) as error:
            message = f"Error in updateProject: {str(error)}"
            exception = str(error)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #######################################################
    # Interface
    @extend_schema(
        summary="Update stuff about the project",
        request=SReqUpdateProject,
        responses={
            200: None,
            400: ExceptionSerializer,
            401: ExceptionSerializer,
            500: ExceptionSerializer
        },
    )
    def patch(self, request):
        return self.updateProject(request)
    
#########################################################################
    ########################################################
    # Delete projects
    ########################################################
    # Serializers

    ########################################################
    # Handler
    def deleteProjects(self, request):
        """
        Delete whole projects

        :param request: DELETE Request
        :type request: HTTP DELETE
        :return: Success or not
        :rtype: HTTPResponse

        """
        try:
            projectIDs = request.GET['projectIDs'].split(",")
            #loggedIn = False # don't check rights in every iteration

            contentManager = ManageContent(request.session)
            interface = contentManager.getCorrectInterface(self.deleteProjects.__name__)
            if interface == None:
                message = "Rights not sufficient in updateProject"
                exception = "Unauthorized"
                logger.error(message)
                exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)

            
            for projectID in projectIDs:
                if not contentManager.checkRightsForProject(projectID):
                    message = "Rights not sufficient in updateProject"
                    exception = "Unauthorized"
                    logger.error(message)
                    exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
                    return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)

                interface.deleteProject(projectID)
                logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},project {projectID}," + str(datetime.now()))
            
            return Response("Success")
        
        except (Exception) as error:
            message = f"Error in deleteProjects: {str(error)}"
            exception = str(error)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #######################################################
    # Interface
    @extend_schema(
        summary="Delete the whole projects",
        request=None,
        responses={
            200: None,
            401: ExceptionSerializer,
            500: ExceptionSerializer
        },
    )
    def delete(self, request):
        return self.deleteProjects(request)
