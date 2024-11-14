"""
Part of Semper-KI software

Akshay NS 2024

Contains: Handlers for processes
"""

import json, logging, copy, numpy
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists, checkIfUserIsLoggedIn, checkIfRightsAreSufficient, manualCheckifAdmin, manualCheckIfRightsAreSufficientForSpecificOperation
from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from code_SemperKI.states.states import StateMachine, signalDependencyToOtherProcesses, processStatusAsInt, ProcessStatusAsString, getButtonsForProcess, getMissingElements
from code_SemperKI.definitions import *
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.utilities.basics import checkIfUserMaySeeProcess
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.connections.content.session import ProcessManagementSession
from code_SemperKI.handlers.public.project import *
from code_SemperKI.logics.processLogics import *
import code_SemperKI.utilities.websocket as WebSocketEvents



logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

#########################################################################
# createProcessID
#"createProcessID": ("public/createProcessID/<str:projectID>", process.createProcessID)
#########################################################################
#TODO Add serializer for createProcessID.  
#######################################################
class SResProcessID(serializers.Serializer):
    processID = serializers.CharField(max_length=200)
#########################################################################
# Handler  
@extend_schema(
    summary="Create a process ID ",
    description="creates a process ID for a given project id",
    request=None,
    tags=['FE - Processes'],
    responses={
        200: SResProcessID,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@loginViaAPITokenIfAvailable()
@api_view(["GET"])
@checkVersion(0.3)
def createProcessID(request:Request, projectID):
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
        interface = contentManager.getCorrectInterface(createProcessID.cls.__name__)
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

        # set default addresses here
        if manualCheckifLoggedIn(request.session):
            clientObject = pgProfiles.ProfileManagementBase.getUser(request.session)
            defaultAddress = {}
            if checkIfNestedKeyExists(clientObject, UserDescription.details, UserDetails.addresses):
                clientAddresses = clientObject[UserDescription.details][UserDetails.addresses]
                for key in clientAddresses:
                    entry = clientAddresses[key]
                    if entry["standard"]:
                        defaultAddress = entry
                        break
            addressesForProcess = {ProcessDetails.clientDeliverAddress: defaultAddress, ProcessDetails.clientBillingAddress: defaultAddress}
            errorOrNot = interface.updateProcess(projectID, processID, ProcessUpdates.processDetails, addressesForProcess, client)
            if isinstance(errorOrNot, Exception):
                raise errorOrNot
        # set default priorities here
        userPrioritiesObject = { prio:{PriorityTargetsSemperKI.value: 4} for prio in PrioritiesForOrganizationSemperKI}
        errorOrNot = interface.updateProcess(projectID, processID, ProcessUpdates.processDetails, {ProcessDetails.priorities: userPrioritiesObject}, client)
        if isinstance(errorOrNot, Exception):
            raise errorOrNot
        # set default title of the process
        errorOrNot = interface.updateProcess(projectID, processID, ProcessUpdates.processDetails, {ProcessDetails.title: processID[:10]}, client)
        if isinstance(errorOrNot, Exception):
            raise errorOrNot


        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

        #return just the id for the frontend
        output = {ProcessDescription.processID: processID}
        outSerializer = SResProcessID(data=output)
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

#########################################################################
# getProcess
#"getProcess": ("public/getProcess/<str:projectID>/<str:processID>/", process.getProcess),
###############serializer#######################################

#######################################################
class SResProcessDetails(serializers.Serializer):
    provisionalContractor = serializers.CharField(max_length=200, required=False)
    amount = serializers.IntegerField(required=False) # deprecated
    inputParameters = serializers.DictField(allow_empty=True, required=False)
    title = serializers.CharField(max_length=200, required=False)
    clientBillingAddress = serializers.DictField(allow_empty=True, required=False)
    clientDeliverAddress = serializers.DictField(allow_empty=True, required=False)
    imagePath = serializers.URLField(required=False)
    priorities = serializers.DictField(allow_empty=True, required=False)

#######################################################
class SResFiles(serializers.Serializer):
    pass

#######################################################
class SResMessages(serializers.Serializer):
    pass

#######################################################
class SResButtonAction(serializers.Serializer):
    type = serializers.CharField(max_length=200)
    data = serializers.DictField()
#######################################################
class SResProcessStatusButtons(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    icon = serializers.CharField(max_length=200)
    action = SResButtonAction()
    active = serializers.BooleanField()
    buttonVariant = serializers.CharField(max_length=200)
    showIn = serializers.CharField(max_length=200)

#######################################################
class SResContractor(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=False)
    hashedID = serializers.CharField(max_length=513, required=False)

#######################################################
class SResProcess(serializers.Serializer):
    processID = serializers.CharField(max_length=200)
    project = serializers.DictField(required=False)
    serviceDetails = serializers.DictField(allow_empty=True, required=False)
    processStatus = serializers.IntegerField()
    serviceType = serializers.IntegerField()
    serviceStatus = serializers.IntegerField()
    processDetails = SResProcessDetails()
    dependenciesIn = serializers.ListField(allow_empty=True, required=False)
    dependenciesOut = serializers.ListField(allow_empty=True, required=False)
    client = serializers.CharField(max_length=513)
    files = serializers.DictField(required=False, allow_empty=True)#SResFiles()
    messages = serializers.DictField(required=False, allow_empty=True)#SResMessages()
    contractor = SResContractor(required=False)
    createdWhen = serializers.CharField(max_length=200)
    updatedWhen = serializers.CharField(max_length=200)
    accessedWhen = serializers.CharField(max_length=200)
    processStatusButtons = serializers.ListField(child=SResProcessStatusButtons(), allow_empty=True)
    processErrors = serializers.ListField(child=serializers.CharField(max_length=200), allow_empty=True)
########################################################
# Handler
@extend_schema(
    summary="Retrieve complete process.",
    description="Retrieve complete process using projectID and processID ",
    request=None,
    tags=['FE - Processes'],
    responses={
        200: SResProcess,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["GET"])
@checkVersion(0.3)
def getProcess(request:Request, projectID, processID):
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

        process = interface.getProcessObj(projectID, processID)
        if isinstance(process, Exception):
            raise process

        # add buttons
        buttons = getButtonsForProcess(process, process.client == userID, adminOrNot) # calls current node of the state machine
        outDict = process.toDict()
        outDict["processStatusButtons"] = buttons

        # add what's missing to continue
        missingElements = getMissingElements(interface, process)
        outDict["processErrors"] = missingElements
        
        outSerializer = SResProcess(data=outDict)
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
        
######################################
#updateProcessFunction
def updateProcessFunction(request:Request, changes:dict, projectID:str, processIDs:list[str]):
    """
    Update process logic
    
    :param projectID: Project ID
    :type projectID: Str
    :param projectID: Process ID
    :type projectID: Str
    :return: Message if it worked or not
    :rtype: Str, bool or Error
    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(updateProcess.cls.__name__)
        if interface == None:
            logger.error("Rights not sufficient in updateProcess")
            return ("", False)
        
        client = contentManager.getClient()
        
        for processID in processIDs:
            if not contentManager.checkRightsForProcess(processID):
                logger.error("Rights not sufficient in updateProcess")
                return ("", False)

            if "deletions" in changes:
                for elem in changes["deletions"]:
                    # exclude people not having sufficient rights for that specific operation
                    if client != GlobalDefaults.anonymous and (elem == ProcessUpdates.messages or elem == ProcessUpdates.files):
                        if not manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.cls.__name__, str(elem)):
                            logger.error("Rights not sufficient in updateProcess")
                            return ("", False)
                        
                    returnVal = interface.deleteFromProcess(projectID, processID, elem, changes["deletions"][elem], client)

                    if isinstance(returnVal, Exception):
                        raise returnVal

            if "changes" in changes:
                for elem in changes["changes"]:
                    fireEvent = False
                    # for websocket events
                    if client != GlobalDefaults.anonymous and (elem == ProcessUpdates.messages or elem == ProcessUpdates.files or elem == ProcessUpdates.processStatus or elem == ProcessUpdates.serviceStatus):
                        # exclude people not having sufficient rights for that specific operation
                        if (elem == ProcessUpdates.messages or elem == ProcessUpdates.files) and not manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.cls.__name__, str(elem)):
                            logger.error("Rights not sufficient in updateProcess")
                            return ("", False)
                        fireEvent = True
                    returnVal = interface.updateProcess(projectID, processID, elem, changes["changes"][elem], client)
                    if isinstance(returnVal, Exception):
                        raise returnVal
                    if fireEvent:
                        if elem == ProcessUpdates.messages:
                            WebSocketEvents.fireWebsocketEventsForProcess(projectID, processID, request.session, elem, returnVal, NotificationSettingsUserSemperKI.newMessage)
                        elif elem == ProcessUpdates.processStatus:
                            WebSocketEvents.fireWebsocketEventsForProcess(projectID, processID, request.session, elem, returnVal, NotificationSettingsUserSemperKI.statusChange)
                        else:
                            WebSocketEvents.fireWebsocketEventsForProcess(projectID, processID, request.session, elem, returnVal)
                    
            # change state for this process if necessary
            process = interface.getProcessObj(projectID, processID)
            currentState = StateMachine(initialAsInt=process.processStatus)
            currentState.onUpdateEvent(interface, process)
            signalDependencyToOtherProcesses(interface, process)

            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.EDITED},updated,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

        return ("", True)
    except (Exception) as error:
        return (error, True)        
        
#########################################################################
# updateProcess
#"updateProcess": ("public/updateProcess/", process.updateProcess),
#########################################################################
# Serializer for updateProcess
#######################################################
class SReqUpdateProcess(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)   
    processIDs = serializers.ListField(child=serializers.CharField(max_length=200))
    changes = serializers.DictField() # TODO: list all updateTypes with optional and such
#########################################################################
# Handler    
@extend_schema(
    summary="Update stuff about the process",
    description=" ",
    request=SReqUpdateProcess,
    tags=['FE - Processes'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["PATCH"])
@checkVersion(0.3)
def updateProcess(request:Request):
    """
    Update stuff about the process

    :param request: Request with content
    :type request: HTTP PATCH
    :return: Message if it worked or not
    :rtype: HTTPResponse

    """
    try:
        inSerializer = SReqUpdateProcess(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {updateProcess.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        changes = inSerializer.data
        projectID = changes["projectID"]
        processIDs = changes["processIDs"] # list of processIDs
        assert projectID != "", f"In {updateProcess.cls.__name__}: non-empty projectID expected"
        assert len(processIDs) != 0, f"In {updateProcess.cls.__name__}: non-empty list of processIDs expected"
        
        # TODO remove
        assert "changes" in changes.keys(), f"In {updateProcess.cls.__name__}: changes not in request"
        if ProcessUpdates.processStatus in changes["changes"]:
            del changes["changes"][ProcessUpdates.processStatus] # frontend shall not change status any more

        message, flag = updateProcessFunction(request, changes, projectID, processIDs)
        if flag is False:
            return Response("Not logged in", status=status.HTTP_401_UNAUTHORIZED)
        if isinstance(message, Exception):
            raise Exception(message)

        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in updateProcess: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################
#deleteProcessFunction
def deleteProcessFunction(session, processIDs:list[str]):
    """
    Delete the processes

    :param session: The session
    :type session: Django session object (dict-like)
    :param processIDs: Array of proccess IDs 
    :type processIDs: list[str]
    :return: The response
    :rtype: HttpResponse | Exception

    """
    try:
        contentManager = ManageContent(session)
        interface = contentManager.getCorrectInterface(deleteProcesses.cls.__name__)
        if interface == None:
            logger.error("Rights not sufficient in deleteProcesses")
            return HttpResponse("Insufficient rights!", status=401)

        for processID in processIDs:
            if not contentManager.checkRightsForProcess(processID):
                logger.error("Rights not sufficient in deleteProcesses")
                return HttpResponse("Insufficient rights!", status=401)
            interface.deleteProcess(processID)
            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))
        return HttpResponse("Success")
    
    except Exception as e:
        return e
            
#########################################################################
# deleteProcess
#"deleteProcesses": ("public/deleteProcesses/<str:projectID>/", process.deleteProcesses),
#########################################################################
#TODO Add serializer for deleteProcess
#########################################################################
# Handler       
@extend_schema(
    summary="Delete one or more processes",
    description=" ",
    request=None,
    tags=['FE - Processes'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    },
    parameters=[OpenApiParameter(
        name='processIDs',
        type={'type': 'array', 'minItems': 1, 'items': {'type': 'string'}},
        location=OpenApiParameter.QUERY,
        required=True,
        style='form',
        explode=False,
    )],
)
@api_view(["DELETE"])
@checkVersion(0.3)
def deleteProcesses(request:Request, projectID):
    """
    Delete one or more processes

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param projectID: id of the project
    :type projectID: str
    :return: Success or not
    :rtype: HTTPRespone

    """
    try:
        processIDs = request.GET['processIDs'].split(",")
        retVal = deleteProcessFunction(request.session, processIDs)
        if isinstance(retVal, Exception):
            raise retVal
        return retVal
    except (Exception) as error:
        message = f"Error in deleteProcesses: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#########################################################################
# getProcessHistory
#"getProcessHistory": ("public/getProcessHistory/<str:processID>/", process.getProcessHistory),
#########################################################################
# serializer for getProcessHistory
#######################################################
class SResHistoryEntry(serializers.Serializer):
    createdBy = serializers.CharField(max_length=200)
    createdWhen = serializers.CharField(max_length=200)
    type = serializers.IntegerField()
    data = serializers.DictField(allow_empty=True)
    details = serializers.DictField(allow_empty=True, required=False)
#######################################################
class SResProcessHistory(serializers.Serializer):
    history = serializers.ListField(child=SResHistoryEntry())
#########################################################################
# Handler           
@extend_schema(
    summary="See who has done what and when",
    description=" ",
    request=None,
    tags=['FE - Processes'],
    responses={
        200: SResHistoryEntry,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["GET"])
@checkVersion(0.3)
def getProcessHistory(request:Request, processID):
    """
    See who has done what and when

    :param request: GET Request
    :type request: HTTP GET
    :param processID: The process of interest
    :type processID: str
    :return: JSON of process history
    :rtype: JSON Response

    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(getProcessHistory.cls.__name__)
        if interface is None:
            logger.error("Rights not sufficient in getProcessHistory")
            return Response("Insufficient rights", status=status.HTTP_401_UNAUTHORIZED)

        processObj = interface.getProcessObj("", processID)
        if processObj is None:
            raise Exception("Process not found in DB!")

        listOfData = interface.getData(processID, processObj)

        outData = []
        for entry in listOfData:
            outDatum = {
                DataDescription.createdBy: entry[DataDescription.createdBy],
                DataDescription.createdWhen: entry[DataDescription.createdWhen],
                DataDescription.type: entry[DataDescription.type],
                DataDescription.data: entry[DataDescription.data] if isinstance(entry[DataDescription.data], dict) else {"value": entry[DataDescription.data]},
                DataDescription.details: entry[DataDescription.details]
            }
            if not isinstance(interface, ProcessManagementSession):
                outDatum[DataDescription.createdBy] = pgProfiles.ProfileManagementBase.getUserNameViaHash(entry[DataDescription.createdBy])
            outData.append(outDatum)

        outObj = {"history": outData}
        outSerializer = SResProcessHistory(data=outObj)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in getProcessHistory: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#########################################################################
# getContractors
#"getContractors": ("public/getContractors/<str:processID>/", process.getContractors),
#########################################################################
#######################################################
class SResContractors(serializers.Serializer):
    hashedID = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)
    details = serializers.DictField()

#########################################################################
# Handler    
@extend_schema(
    summary="Get all suitable Contractors",
    description=" ",
    tags=['FE - Processes'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResContractors),
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=True)
@checkIfUserMaySeeProcess(json=True)
@api_view(["GET"])
@checkVersion(0.3)
def getContractors(request:Request, processID:str):
    """
    Get all suitable Contractors.

    :param request: GET request
    :type request: HTTP GET
    :param processID: The ID of the process a contractor is chosen for
    :type processID: str
    :return: List of contractors and some details
    :rtype: JSON

    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface() # checks not needed for rights, was done in the decorators
        processObj = interface.getProcessObj("", processID) # Login was required here so projectID not necessary
        if processObj == None:
            raise Exception("Process ID not found in session or db")
 
        listOfResultingContractors, pricePerContractor = logicForGetContractors(processObj)
        # TODO
        outSerializer = SResContractors(data=listOfResultingContractors, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in getContractors: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        
#########################################################################
# cloneProcess
#########################################################################
#TODO Add serializer for cloneProcess
#######################################################
class SResCloneProcess(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    processIDs = serializers.ListField(child=serializers.CharField(max_length=200))
#########################################################################
# Handler    
@extend_schema(
    summary="Duplicate selected processes. Works only for logged in users.",
    description=" ",
    tags=['FE - Processes'],
    request=None,
    responses={
        200: SResCloneProcess,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=True)
@api_view(["GET"])
@checkVersion(0.3)
def cloneProcess(request:Request, oldProjectID:str, oldProcessIDs:list[str]):
    """
    Duplicate selected processes. Works only for logged in users.

    :param request: POST request from statusButtonRequest
    :type request: HTTP POST
    :param projectID: The project ID of the project the processes belonged to
    :type projectID: str
    :param processIDs: List of processes to be cloned
    :type processIDs: list of strings
    :return: JSON with project and process IDs
    :rtype: JSONResponse
    
    """
    try:
        outDict = {"projectID": "", "processIDs": []}

        # create new project with old information
        oldProject = pgProcesses.ProcessManagementBase.getProjectObj(oldProjectID)
        newProjectID = crypto.generateURLFriendlyRandomString()
        outDict["projectID"] = newProjectID
        errorOrNone = pgProcesses.ProcessManagementBase.createProject(newProjectID, oldProject.client)
        if isinstance(errorOrNone, Exception):
            raise errorOrNone
        pgProcesses.ProcessManagementBase.updateProject(newProjectID, ProjectUpdates.projectDetails, oldProject.projectDetails)
        if isinstance(errorOrNone, Exception):
            raise errorOrNone
        
        mapOfOldProcessIDsToNewOnes = {}
        # for every old process, create new process with old information
        for processID in oldProcessIDs:
            oldProcess = pgProcesses.ProcessManagementBase.getProcessObj(oldProjectID, processID) 
            newProcessID = crypto.generateURLFriendlyRandomString()
            outDict["processIDs"].append(newProcessID)
            mapOfOldProcessIDsToNewOnes[processID] = newProcessID
            errorOrNone = pgProcesses.ProcessManagementBase.createProcess(newProjectID, newProcessID, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            
            oldProcessDetails = copy.deepcopy(oldProcess.processDetails)
            del oldProcessDetails[ProcessDetails.provisionalContractor]
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.processDetails, oldProcessDetails, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            
            # copy files but with new fileID
            newFileDict = {}
            for fileKey in oldProcess.files:
                oldFile = oldProcess.files[fileKey]
                newFile = copy.deepcopy(oldFile)
                #newFileID = crypto.generateURLFriendlyRandomString()
                newFile[FileObjectContent.id] = fileKey
                newFilePath = newProcessID+"/"+fileKey
                newFile[FileObjectContent.path] = newFilePath
                newFile[FileObjectContent.date] = str(timezone.now())
                if FileObjectContent.isFile not in newFile or newFile[FileObjectContent.isFile]:
                    if oldFile[FileObjectContent.remote]:
                        s3.manageRemoteS3.copyFile("kiss/"+oldFile[FileObjectContent.path], newFilePath)
                    else:
                        s3.manageLocalS3.copyFile(oldFile[FileObjectContent.path], newFilePath)
                newFileDict[fileKey] = newFile
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.files, newFileDict, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            
            # set service specific stuff
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.serviceType, oldProcess.serviceType, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            # set service details -> implementation in service (cloneServiceDetails)
            newProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, newProcessID) 
            errorOrNewDetails = serviceManager.getService(oldProcess.serviceType).cloneServiceDetails(oldProcess.serviceDetails, newProcess)
            if isinstance(errorOrNewDetails, Exception):
                raise errorOrNewDetails
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.serviceDetails, errorOrNewDetails, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone

        # all new processes must already be created here in order to link them accordingly
        for oldProcessID in mapOfOldProcessIDsToNewOnes:
            newProcessID = mapOfOldProcessIDsToNewOnes[oldProcessID]
            oldProcess = pgProcesses.ProcessManagementBase.getProcessObj(oldProjectID, oldProcessID)
            newProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, newProcessID)
            # connect the processes if they where dependend before
            for connectedOldProcessIn in oldProcess.dependenciesIn.all():
                if connectedOldProcessIn.processID in oldProcessIDs:
                    newConnectedProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, mapOfOldProcessIDsToNewOnes[connectedOldProcessIn.processID])
                    newProcess.dependenciesIn.add(newConnectedProcess)
            for connectedOldProcessIn in oldProcess.dependenciesOut.all():
                if connectedOldProcessIn.processID in oldProcessIDs:
                    newConnectedProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, mapOfOldProcessIDsToNewOnes[connectedOldProcessIn.processID])
                    newProcess.dependenciesOut.add(newConnectedProcess)
            newProcess.save()

            # set process state through state machine (could be complete or waiting or in conflict and so on)
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.SERVICE_IN_PROGRESS), oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            newProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, newProcessID)
            currentState = StateMachine(initialAsInt=newProcess.processStatus)
            contentManager = ManageContent(request.session)
            interface = contentManager.getCorrectInterface(cloneProcess.cls.__name__)
            currentState.onUpdateEvent(interface, newProcess)

        outSerializer = SResCloneProcess(data=outDict)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
        
    except Exception as error:
        message = f"Error in getContractors: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
