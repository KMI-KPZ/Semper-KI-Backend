"""
Part of Semper-KI software

Akshay NS 2024

Contains: Handlers for processes
"""

import json, logging
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter


from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, manualCheckifAdmin
from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from code_SemperKI.states.states import getButtonsForProcess

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.utilities.basics import ExceptionSerializer
from code_SemperKI.handlers.public.project import *
from code_SemperKI.handlers.projectAndProcessManagement import updateProcessFunction, deleteProcessFunction

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
#############



#########Serializer#############
#TODO Add serializer for createProcessID.
#######################################################
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
        assert isinstance(processID, str), f"In {createProcessID.__name__}: expected processID to be of type string, instead got: {type(processID)}"
        assert processID != "", f"In {createProcessID.__name__}: non-empty processID expected"
        
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
        
        

###serializer###########
#TODO Add serializer for getProcess
#######################################################
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
# @checkIfUserIsLoggedIn()
# @require_http_methods(["GET"])
# @checkIfRightsAreSufficient(json=False)
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
        assert isinstance(userID, str), f"In {getProcess.__name__}: expected userID to be of type string, instead got: {type(userID)}"
        assert userID != "", f"In {getProcess.__name__}: non-empty userID expected"
        adminOrNot = manualCheckifAdmin(request.session)
        assert isinstance(adminOrNot, bool), f"In {getProcess.__name__}: expected adminOrNot to be of type bool, instead got {type(adminOrNot)}"
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
        
####################    
#########Serializer#############
#TODO Add serializer
# "updateProcess": ("public/updateProcess/", process.updateProcess),
#######################################################
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
# @checkIfUserIsLoggedIn()
# @require_http_methods(["PATCH"])
# @checkIfRightsAreSufficient(json=False)
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
        assert "projectID" in changes.keys(), f"In {updateProcess.__name__}: projectID not in request"
        assert "projectIDs" in changes.keys(), f"In {updateProcess.__name__}: projectIDs not in request"
        projectID = changes["projectID"]
        processIDs = changes["processIDs"] # list of processIDs
        
        # TODO remove
        assert "changes" in changes.keys(), f"In {updateProcess.__name__}: changes not in request"
        if ProcessUpdates.processStatus in changes["changes"]:
            del changes["changes"][ProcessUpdates.processStatus] # frontend shall not change status any more

        message, flag = updateProcessFunction(request, changes, projectID, processIDs)
        assert isinstance(message, str), f"In {updateProcess.__name__}: expected message to be of type string instead got {type(message)}"
        assert isinstance(flag, bool), f"In {updateProcess.__name__}: expected flag to be of type bool instead got {type(message)}"
        if flag is False:
            return Response("Not logged in", status=status.HTTP_401_UNAUTHORIZED)
        if isinstance(message, Exception):
            raise Exception(message)

        return HttpResponse("Success")
    except (Exception) as error:
        message = f"Error in updateProcess: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#########Serializer#############
#TODO Add serializer    
# "deleteProcesses": ("public/deleteProcesses/", process.deleteProcesses),
#######################################################
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
# @checkIfUserIsLoggedIn()
# @require_http_methods(["DELETE"])
# @checkIfRightsAreSufficient(json=False)
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
        

#########Serializer#############
#TODO Add serializer        
# "getProcessHistory": ("public/getProcessHistory/", process.getProcessHistory),
#######################################################
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

        return Response(outObj, status.status_code.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in getProcessHistory: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
#########Serializer#############
#TODO Add serializer  
#######################################################
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