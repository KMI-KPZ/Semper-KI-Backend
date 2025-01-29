"""
Part of Semper-KI software

Akshay NS 2024

Contains: Handlers for processes
"""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Generic_Backend.code_General.definitions import *

from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import checkIfUserMaySeeProcess
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.manageContent import ManageContent

from code_SemperKI.connections.content.session import ProcessManagementSession
from code_SemperKI.handlers.public.project import *
from code_SemperKI.logics.processLogics import *


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
        result, statusCode = logicForCreateProcessID(request, projectID, createProcessID.cls.__name__)
        if isinstance(result, Exception):
            message = f"Error in {createProcessID.cls.__name__}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        outSerializer = SResProcessID(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {createProcessID.cls.__name__}: {str(error)}"
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
    provisionalContractor = serializers.DictField(allow_empty=True, required=False)
    amount = serializers.IntegerField(required=False) # deprecated
    inputParameters = serializers.DictField(allow_empty=True, required=False)
    title = serializers.CharField(max_length=200, required=False)
    clientBillingAddress = serializers.DictField(allow_empty=True, required=False)
    clientDeliverAddress = serializers.DictField(allow_empty=True, required=False)
    imagePath = serializers.URLField(required=False)
    priorities = serializers.DictField(allow_empty=True, required=False)
    prices = serializers.DictField(allow_empty=True, required=False)

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
    iconPosition = serializers.CharField(max_length=200)
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
    contractor = SResContractor(required=False, allow_null=True)
    createdWhen = serializers.CharField(max_length=200)
    updatedWhen = serializers.CharField(max_length=200)
    accessedWhen = serializers.CharField(max_length=200)
    processStatusButtons = serializers.ListField(child=SResProcessStatusButtons(), allow_empty=True)
    processErrors = serializers.ListField(child=serializers.DictField(allow_empty=True), allow_empty=True)
    flatProcessStatus = serializers.CharField(max_length=200, allow_blank=True, required=False)
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
        outDict, statusCode = logicForGetProcess(request, projectID, processID, getProcess.cls.__name__)
        if isinstance(outDict, Exception):
            message = "Error in getProcess"
            exception = str(outDict)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
        
 
#########################################################################
# updateProcess
#"updateProcess": ("public/updateProcess/", process.updateProcess),
#########################################################################
# Serializer for updateProcess
#######################################################
class SReqUpdateProcess(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)   
    processIDs = serializers.ListField(child=serializers.CharField(max_length=200))
    changes = serializers.DictField(required=False, allow_empty=True) # TODO: list all updateTypes with optional and such
    deletions = serializers.DictField(required=False, allow_empty=True)
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
        
        if "changes" in changes and ProcessUpdates.processStatus in changes["changes"]:
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
    branding = serializers.DictField()
    prices = serializers.DictField()
    distance = serializers.FloatField()
    contractorCoordinates = serializers.ListField(child=serializers.FloatField(), required=False)


#########################################################################
# Handler    
@extend_schema(
    summary="Get all suitable Contractors",
    description=" ",
    tags=['FE - Processes'],
    request=None,
    responses={
        200: serializers.ListSerializer(child=SResContractors()),
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
 
        listOfResultingContractors, statusCode = logicForGetContractors(processObj)
        if isinstance(listOfResultingContractors, Exception):
            message = "Error in getContractors"
            exception = str(listOfResultingContractors)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
class SReqsCloneProcess(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    processIDs = serializers.ListField(child=serializers.CharField(max_length=200))
#########################################################################
# Handler    
@extend_schema(
    summary="Duplicate selected processes. Works only for logged in users.",
    description=" ",
    tags=['FE - Processes'],
    request=SReqsCloneProcess,
    responses={
        200: SReqsCloneProcess,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=True)
@api_view(["POST"])
@checkVersion(0.3)
def cloneProcesses(request:Request):
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
        inSerializer = SReqsCloneProcess(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {cloneProcesses.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        validatedInput = inSerializer.data
        oldProjectID = validatedInput["projectID"]
        oldProcessIDs = validatedInput["processIDs"]
        result, statusCode = logicForCloneProcesses(request, oldProjectID, oldProcessIDs, cloneProcesses.cls.__name__)
        if isinstance(result, Exception):
            message = f"Error in {cloneProcesses.cls.__name__}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        outSerializer = SReqsCloneProcess(data=result)
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
