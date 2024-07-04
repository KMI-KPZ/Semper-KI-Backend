"""
Part of Semper-KI software

Akshay NS 2024

Contains: Handlers for processes
"""

import json, logging, copy
import json, logging, copy
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

from code_SemperKI.states.states import StateMachine, signalDependencyToOtherProcesses, processStatusAsInt, ProcessStatusAsString, getButtonsForProcess
from code_SemperKI.definitions import *
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.utilities.basics import checkIfUserMaySeeProcess
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.handlers.public.project import *
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
    tags=['Processes'],
    responses={
        200: SResProcessID,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
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

        # set default addresses here
        if manualCheckifLoggedIn(request.session):
            clientObject = pgProfiles.ProfileManagementBase.getUser(request.session)
            defaultAddress = {"undefined": {}}
            if checkIfNestedKeyExists(clientObject, UserDescription.details, UserDetails.addresses):
                clientAddresses = clientObject[UserDescription.details][UserDetails.addresses]
                for key in clientAddresses:
                    entry = clientAddresses[key]
                    if entry["standard"]:
                        defaultAddress = entry
                        break
            addressesForProcess = {ProcessDetails.clientDeliverAddress: defaultAddress, ProcessDetails.clientBillingAddress: defaultAddress}
            interface.updateProcess(projectID, processID, ProcessUpdates.processDetails, addressesForProcess, client)


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
#TODO Add serializer for getProcess
########################################################
# Handler
@extend_schema(
    summary="Retrieve complete process.",
    description="Retrieve complete process using projectID and processID ",
    request=None,
    tags=['Processes'],
    responses={
        200: None,
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

        buttons = getButtonsForProcess(process, process.client == userID, adminOrNot) # calls current node of the state machine
        outDict = process.toDict()
        outDict["processStatusButtons"] = buttons
        ###TODO: add outserializers.
        return Response(outDict, status=status.HTTP_200_OK)
        # outSerializer = SResGetProcess(data=process)
        # if outSerializer.is_valid():
        #     return Response(outSerializer.data, status=status.HTTP_200_OK)
        # else:
        #     raise Exception(outSerializer.errors)    
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
        interface = contentManager.getCorrectInterface(updateProcess.__name__)
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
                        if not manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, str(elem)):
                            logger.error("Rights not sufficient in updateProcess")
                            return ("", False)
                        
                    returnVal = interface.deleteFromProcess(projectID, processID, elem, changes["deletions"][elem], client)

                    if isinstance(returnVal, Exception):
                        raise returnVal

            if "changes" in changes:
                for elem in changes["changes"]:
                    # for websocket events
                    if client != GlobalDefaults.anonymous and (elem == ProcessUpdates.messages or elem == ProcessUpdates.files or elem == ProcessUpdates.processStatus or elem == ProcessUpdates.serviceStatus):
                        # exclude people not having sufficient rights for that specific operation
                        if (elem == ProcessUpdates.messages or elem == ProcessUpdates.files) and not manualCheckIfRightsAreSufficientForSpecificOperation(request.session, updateProcess.__name__, str(elem)):
                            logger.error("Rights not sufficient in updateProcess")
                            return ("", False)
                        WebSocketEvents.fireWebsocketEvents(projectID, [processID], request.session, elem, elem)
                    
                    returnVal = interface.updateProcess(projectID, processID, elem, changes["changes"][elem], client)
                    if isinstance(returnVal, Exception):
                        raise returnVal
            
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
    tags=['Processes'],
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
            exception = "Verification failed"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        changes = inSerializer.data
        projectID = changes["projectID"]
        processIDs = changes["processIDs"] # list of processIDs
        
        # TODO remove
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
    tags=['Processes'],
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
        processIDs = request.data['processIDs']
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
#TODO Add serializer for getProcessHistory
#######################################################
class SResHistoryEntry(serializers.Serializer):
    createdBy = serializers.CharField(max_length=200)
    createdWhen = serializers.CharField(max_length=200)
    type = serializers.IntegerField()
    data = serializers.DictField()
#######################################################
class SResProcessHistory(serializers.Serializer):
    history = serializers.ListField(child=SResHistoryEntry())
#########################################################################
# Handler           
@extend_schema(
    summary="See who has done what and when",
    description=" ",
    request=None,
    tags=['Processes'],
    responses={
        200: SResHistoryEntry,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=True)
@checkIfUserMaySeeProcess(json=True)
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
        processObj = pgProcesses.ProcessManagementBase.getProcessObj("", processID)

        if processObj == None:
            raise Exception("Process not found in DB!")
        
        listOfData = pgProcesses.ProcessManagementBase.getData(processID, processObj)
        # parse for frontend
        for index, entry in enumerate(listOfData):
            outDatum = {}
            outDatum[DataDescription.createdBy] = pgProfiles.ProfileManagementBase.getUserNameViaHash(entry[DataDescription.createdBy])
            outDatum[DataDescription.createdWhen] = entry[DataDescription.createdWhen]
            outDatum[DataDescription.type] = entry[DataDescription.type]
            outDatum[DataDescription.data] = entry[DataDescription.data]
            listOfData[index] = outDatum # overwrite

        outObj = {"history": listOfData}
        outSerializer = SResHistoryEntry(data=outObj)
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
#TODO Add serializer for getContractors
#########################################################################
# Handler    
@extend_schema(
    summary="Get all suitable Contractors",
    description=" ",
    tags=['Processes'],
    request=None,
    responses={
        200: None,
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
 
        serviceType = processObj.serviceType
        service = serviceManager.getService(processObj.serviceType)

        listOfFilteredContractors = service.getFilteredContractors(processObj)
        # Format coming back from SPARQL is [{"ServiceProviderName": {"type": "literal", "value": "..."}, "ID": {"type": "literal", "value": "..."}}]
        # Therefore parse it
        listOfResultingContractors = []
        for contractor in listOfFilteredContractors:
            idOfContractor = contractor["ID"]["value"]
            contractorContentFromDB = pgProfiles.ProfileManagementOrganization.getOrganization(hashedID=idOfContractor)
            if isinstance(contractorContentFromDB, Exception):
                raise contractorContentFromDB
            contractorToBeAdded = {OrganizationDescription.hashedID: contractorContentFromDB[OrganizationDescription.hashedID],
                                   OrganizationDescription.name: contractorContentFromDB[OrganizationDescription.name]+"_filtered",
                                   OrganizationDescription.details: contractorContentFromDB[OrganizationDescription.details]}
            listOfResultingContractors.append(contractorToBeAdded)
        
        if len(listOfFilteredContractors) == 0 or settings.DEBUG:
            listOfResultingContractors.extend(pgProcesses.ProcessManagementBase.getAllContractors(serviceType))

        # TODO add serializers
        return JsonResponse(listOfResultingContractors, safe=False)
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
    tags=['Processes'],
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
