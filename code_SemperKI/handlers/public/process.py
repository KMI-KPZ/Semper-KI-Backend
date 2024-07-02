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
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, manualCheckifAdmin, manualCheckIfRightsAreSufficientForSpecificOperation
from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, manualCheckifAdmin, manualCheckIfRightsAreSufficientForSpecificOperation
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
from code_SemperKI.handlers.public.websocket import fireWebsocketEvents



logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################


#########################################################################
# createProcessID
#########################################################################
#TODO Add serializer for createProcessID.  
#########################################################################
# Handler  
@extend_schema(
    summary="Create a process ID ",
    description="creates a process ID for a given project id",
    request=None,
    tags=['process'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["GET"])
def createProcessID(request, projectID):
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

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

        #return just the id for the frontend
        #TODO add outseriliazer for createProcessID.
        output = {ProcessDescription.processID: processID}
        return Response(output, status=status.HTTP_200_OK)
        # outSerializer = SResCreateProcessID(data=output)
        # if outSerializer.is_valid():
        #     return Response(outSerializer.data, status=status.HTTP_200_OK)
        # else:
        #     raise Exception(outSerializer.errors)
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
###serializer###########
#TODO Add serializer for getProcess
########################################################
# Handler
@extend_schema(
    summary="Retrieve complete process.",
    description="Retrieve complete process using projectID and processID ",
    request=None,
    tags=['process'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["GET"])
def getProcess(request, projectID, processID):
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

        process = interface.getProcess(projectID, processID)
        if process != {}:
            buttons = getButtonsForProcess(process[ProcessDescription.processStatus], process[ProcessDescription.client] == userID, adminOrNot) # calls current node of the state machine
            process["processStatusButtons"] = buttons
        ###TODO: add outserializers.
        return Response(process, status=status.HTTP_200_OK)
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
def updateProcessFunction(request, changes:dict, projectID:str, processIDs:list[str]):
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
                        fireWebsocketEvents(projectID, [processID], request.session, elem, elem)
                    
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
#########################################################################
#TODO Add serializer for updateProcess
#########################################################################
# Handler    
@extend_schema(
    summary="Update stuff about the process",
    description=" ",
    request=None,
    tags=['process'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["PATCH"])
def updateProcess(request):
    """
    Update stuff about the process

    :param request: Request with content
    :type request: HTTP PATCH
    :return: Message if it worked or not
    :rtype: HTTPResponse

    """
    try:
        changes = json.loads(request.body.decode("utf-8"))
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
#########################################################################
#TODO Add serializer for deleteProcess
#########################################################################
# Handler       
@extend_schema(
    summary="Delete one or more processes",
    description=" ",
    request=None,
    tags=['process'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["DELETE"])
def deleteProcesses(request, projectID):
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
#########################################################################
#TODO Add serializer for getProcessHistory
#########################################################################
# Handler           
@extend_schema(
    summary="See who has done what and when",
    description=" ",
    request=None,
    tags=['process'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=True)
@checkIfUserMaySeeProcess(json=True)
@api_view(["GET"])
def getProcessHistory(request, processID):
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

        return Response(outObj, status=status.HTTP_200_OK)
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
#########################################################################
#TODO Add serializer for getContractors
#########################################################################
# Handler    
@extend_schema(
    summary="Get all suitable Contractors",
    description=" ",
    tags=['process'],
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
def getContractors(request, processID:str):
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


        listOfAllContractors = pgProcesses.ProcessManagementBase.getAllContractors(serviceType)
        # TODO Check suitability

        # remove unnecessary information and add identifier
        # for idx, elem in enumerate(listOfAllContractors):
        #     contractorList.append({})
        #     contractorList[idx]["name"] = elem["name"]
        #     contractorList[idx]["id"] = elem["hashedID"]

        return JsonResponse(listOfAllContractors, safe=False)
    except (Exception) as error:
        message = f"Error in getContractors: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        
#######################################
#########################################################################
# cloneProcess
def cloneProcess(request, oldProjectID:str, oldProcessIDs:list[str]):
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

        return JsonResponse(outDict)
        
    except Exception as error:
        loggerError.error(f"Error when cloning processes: {error}")
        return JsonResponse({})
    
############################################################
def getProcessAndProjectFromSession(session, processID):
    """
    Retrieve a specific process from the current session instead of the database
    
    :param session: Session of the current user
    :type session: Dict
    :param projectID: Process ID
    :type projectID: Str
    :return: Process or None
    :rtype: Dict or None
    """
    try:
        contentManager = ManageContent(session)
        if contentManager.sessionManagement.getIfContentIsInSession():
            return contentManager.sessionManagement.structuredSessionObj.getProcessAndProjectPerID(processID)
        else:
            return (None, None)
    except (Exception) as error:
        loggerError.error(f"getProcessAndProjectFromSession: {str(error)}")
        return (None, None)