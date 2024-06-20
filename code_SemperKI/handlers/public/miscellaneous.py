"""
Part of Semper-KI software

Akshay NS 2024

Contains: Handlers for miscellaneous
"""

import logging, zipfile, base64, math
import os
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings

from boto3.s3.transfer import TransferConfig
from botocore.response import StreamingBody
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, manualCheckifLoggedIn, manualCheckifAdmin, manualCheckIfRightsAreSufficient, manualCheckIfRightsAreSufficientForSpecificOperation
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.utilities.files import createFileResponse
from Generic_Backend.code_General.utilities.crypto import EncryptionAdapter

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from Generic_Backend.code_General.utilities import crypto
from code_SemperKI.serviceManager import serviceManager
import code_SemperKI.connections.content.manageContent as ManageC
from code_SemperKI.connections.content.manageContent import ManageContent
import code_SemperKI.handlers.projectAndProcessManagement as PPManagement
from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.states.states import processStatusAsInt, ProcessStatusAsString, StateMachine, getButtonsForProcess, InterfaceForStateChange


logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
loggerDebug = logging.getLogger("django_debug")
##################################################

#########Serializer#############
#TODO Add serializer  
# "getServices": ("public/getServices/", miscellaneous.getServices),
#######################################################
@extend_schema(
    summary="Return the offered services",
    description=" ",
    request=None,
    tags = ['miscellaneous'],
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
def getServices(request):
    """
    Return the offered services
downloadFileStream), #
    :param request: The request object
    :type request: Dict
    :return: The Services as dictionary with string and integer coding
    :rtype: JSONResponse
    
    """
    try:
        output = serviceManager.getAllServices()
        return Response(output, status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in getServices: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
#########Serializer#############
#TODO Add serializer  
 
#  "uploadFiles": ("public/uploadFiles/", miscellaneous.uploadFiles),
 #######################################################
@extend_schema(
     summary="File upload for a process",
     description=" ",
     request=None,
     tags=['files'],
     responses={
         200: None,
         401: ExceptionSerializer,
         500: ExceptionSerializer
     }
 )

@api_view(["POST"])
def uploadFiles(request):
    """
    File upload for a process

    :param request: Request with files in it
    :type request: HTTP POST
    :return: Successful or not
    :rtype: HTTP Response
    """
    try:
        info = request.POST
        projectID = info["projectID"]
        processID = info["processID"]
        # TODO: Licenses, ...

        content = ManageC.ManageContent(request.session)
        interface = content.getCorrectInterface(uploadFiles.cls.__name__)
        if interface.checkIfFilesAreRemote(projectID, processID):
            remote = True
        else:
            remote = False

        fileNames = list(request.FILES.keys())
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
        changes = {"changes": {ProcessUpdates.files: {}}}
        for fileName in fileNames:
            fileID = crypto.generateURLFriendlyRandomString()
            filePath = processID+"/"+fileID
            changes["changes"][ProcessUpdates.files][fileID] = {}
            changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.id] = fileID
            changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.fileName] = fileName
            changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.date] = str(timezone.now())
            changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.createdBy] = userName
            changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.path] = filePath
            if remote:
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.remote] = True
                returnVal = s3.manageRemoteS3.uploadFile(filePath, request.FILES.getlist(fileName)[0])
                if returnVal is not True:
                    return Response("Failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.remote] = False
                returnVal = s3.manageLocalS3.uploadFile(filePath, request.FILES.getlist(fileName)[0])
                if returnVal is not True:
                    return Response("Failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Save into files field of the process
        message, flag = PPManagement.updateProcessFunction(request, changes, projectID, [processID])
        if flag is False:
            return Response("Insufficient rights!", status=status.HTTP_401_UNAUTHORIZED)
        if isinstance(message, Exception):
            raise message

        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},files,"+str(datetime.now()))
        return Response('Success', status=status.HTTP_200_OK)
        
    except (Exception) as error:
        message = f"Error while uploading files: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
###################################################################################
def getFileReadableStream(request, projectID, processID, fileID) -> tuple[EncryptionAdapter, bool]:
    """
    Get file from storage and return it as readable object where the content can be read in desired chunks
    (will be decrypted if necessary)

    :param request: Request of user for a specific file of a process
    :type request: HTTP POST
    :param projectID: Project ID
    :type projectID: str
    :param processID: process ID
    :type processID: Str
    :param fileID: file ID
    :type fileID: Str
    :return: Saved content
    :rtype: EncryptionAdapter

    """
    try:
        fileObj, flag, isRemote = getFileObject(request, projectID, processID, fileID)
        if flag is False:
            return (None, False)

        if not flag:
            logger.warning(f"File {fileID} not found in process {processID}")
            return  (None, False)

        if not "Body" in fileObj:
            logger.warning(f"Error while accessing stream object in file {fileID} of process {processID}")
            return (None, False)

        streamingBody = fileObj['Body']
        if not isinstance(streamingBody, StreamingBody):
            logger.warning(f"Error while accessing streaming body in file {fileID} of process {processID}")
            return (None, False)

        encryptionAdapter = EncryptionAdapter(streamingBody)

        if isRemote is False:
            # local files are not encrypted
            return (encryptionAdapter, True)

        encryptionAdapter.setupDecryptOnRead(base64.b64decode(s3.manageRemoteS3.aesEncryptionKey))

        return (encryptionAdapter, True)

    except (Exception) as error:
        loggerError.error(f"Error while accessing and streaming file: {str(error)}")
        return (None, False)
    
    
def getFileObject(request, projectID, processID, fileID) -> tuple[object, bool, bool]:
    """
    Get file from storage and return it as accessible object - you have to decrypt it if necessary

    :param request: Request of user for a specific file of a process
    :type request: HttpRequest
    :param projectID: Project ID
    :type projectID: str
    :param processID: process ID
    :type processID: Str
    :param fileID: file ID
    :type fileID: Str
    :return: (fileObject from S3, retrieval success, is remote location)
    :rtype: (object, bool, bool)

    """
    try:
        isRemote = False
        fileOfThisProcess, flag = getFilesInfoFromProcess(request, projectID, processID, fileID)
        if flag is False:
            return (None, False, False)

        # retrieve the correct file object
        if fileOfThisProcess[FileObjectContent.remote]:
            fileObj, flag = s3.manageRemoteS3.getFileObject(fileOfThisProcess[FileObjectContent.path])
            if flag is False:
                logger.warning(f"File {fileID} not found in process {processID}")
                return (None, False, False)
            isRemote = True
        else:
            fileObj, flag = s3.manageLocalS3.getFileObject(fileOfThisProcess[FileObjectContent.path])
            if flag is False:
                logger.warning(f"File {fileID} not found in process {processID}")
                return (None, False, False)
            
        logger.info(
            f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},"
            f"{Logging.Predicate.FETCHED},accessed,{Logging.Object.OBJECT},file {fileOfThisProcess[FileObjectContent.fileName]}," + str(
                datetime.now()))

        return (fileObj, True, isRemote)

    except (Exception) as error:
        loggerError.error(f"Error while downloading file: {str(error)}")
        return (None,False, False)  
      
#########Serializer#############
#TODO Add serializer  
# "getFilesInfoFromProcess": ("public/getFilesInfoFromProc/", miscellaneous.getFilesInfoFromProcess),
@extend_schema(
    summary="Obtain file(s) information from a process",
    description=" ",
    tags="files",
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer,
        404: ExceptionSerializer
    }
)
# @checkIfUserIsLoggedIn()
# @require_http_methods(["POST"])
# @checkIfRightsAreSufficient(json=False)
@api_view(["POST"])
def getFilesInfoFromProcess(request, projectID, processID, fileID) -> tuple[object, bool]:
    """
    Obtain file(s) information from a process

    :param request: Request of user for a specific file of a process
    :type request: HTTP POST
    :param projectID: Project ID
    :type projectID: str
    :param processID: process ID
    :type processID: Str
    :param fileID: file ID, if given then only that file is returned, else all files
    :type fileID: Str
    :return: file metadata or Error HttpResponse  , retrieval success
    :rtype: (dict|HttpResponse, bool)

    """
    try:
        # Retrieve the files info from either the session or the database
        contentManager = ManageC.ManageContent(request.session)
        interface = contentManager.getCorrectInterface(downloadFileStream.cls.__name__)
        if interface == None:
            return (Response("Not logged in or rights insufficient!", status=status.HTTP_401_UNAUTHORIZED),False)
        
        if not contentManager.checkRightsForProcess(processID):
            return (Response("Not allowed to see process!", status=status.HTTP_401_UNAUTHORIZED),False)

        currentProcess = interface.getProcessObj(projectID, processID)
        if currentProcess == None:
            return (Response("Not found!", status=status.HTTP_404_NOT_FOUND), False)
        
        if fileID != "":
            if fileID not in currentProcess.files:
                return (Response("Not found!", status=status.HTTP_404_NOT_FOUND),False)
            
            fileOfThisProcess = currentProcess.files[fileID]
            return (fileOfThisProcess, True)
        else:
            return (currentProcess.files, True)
    except (Exception) as error:
        message = f"Error in getFilesInfoFromProcess: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#########Serializer#############
#TODO Add serializer  
# "downloadFileStream": ("public/downloadFileStream/", miscellaneous.downloadFileStream),
#######################################################
@extend_schema(
    summary="Send file to user from storage",
    description="Send file to user from storage with request of user for a specific file of a process  ",
    tags=["files"],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@api_view(["GET"])
def downloadFileStream(request, projectID, processID, fileID):
    """
    Send file to user from storage

    :param request: Request of user for a specific file of a process
    :type request: HTTP POST
    :param projectID: Project ID
    :type projectID: str
    :param processID: process ID
    :type processID: Str
    :param fileID: file ID
    :type fileID: Str
    :return: Saved content
    :rtype: FileResponse

    """
    try:
        fileMetaData, flag = getFilesInfoFromProcess(request, projectID, processID, fileID)
        if flag is False:
            return fileMetaData

        encryptionAdapter, flag = getFileReadableStream(request, projectID, processID, fileID)
        if flag is False:
            return Response("Failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if os.getenv("DJANGO_LOG_LEVEL", None) == "DEBUG":
            encryptionAdapter.setDebugLogger(loggerDebug)

        return createFileResponse(encryptionAdapter, filename=fileMetaData[FileObjectContent.fileName])
    
    except (Exception) as error:
        message = f"Error in downloadFileStream: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        
        
#########Serializer#############
#TODO Add serializer  
# "downloadFilesAsZip": ("public/downloadFilesAsZip/", miscellaneous.downloadFilesAsZip),
#######################################################
@extend_schema(
    summary="Send files to user as zip",
    description=" ",
    tags=["files"],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer,
        404: ExceptionSerializer
    }
)

@api_view(["GET"])
def downloadFilesAsZip(request, projectID, processID):
    """
    Send files to user as zip

    :param request: Request of user for all selected files of a process
    :type request: HTTP POST
    :param projectID: Project ID
    :type projectID: str
    :param processID: process ID
    :type processID: Str
    :return: Saved content
    :rtype: FileResponse

    """
     # TODO solve with streaming
    try:
        fileIDs = request.GET['fileIDs'].split(",")
        filesArray = []

        # Retrieve the files infos from either the session or the database
        filesOfThisProcess, flag = getFilesInfoFromProcess(request, projectID, processID)
        if flag is False:
            return filesOfThisProcess # will be HTTPResponse
        
        # get files, download them from aws, put them in an array together with their name
        for elem in filesOfThisProcess:
            currentEntry = filesOfThisProcess[elem]
            if FileObjectContent.id in currentEntry and currentEntry[FileObjectContent.id] in fileIDs:
                content, flag = s3.manageLocalS3.downloadFile(currentEntry[FileObjectContent.path])
                if flag is False:
                    content, flag = s3.manageRemoteS3.downloadFile(currentEntry[FileObjectContent.path])
                    if flag is False:
                        return Response("Not found!", status=status.HTTP_404_NOT_FOUND)
                
                filesArray.append( (currentEntry[FileObjectContent.fileName], content) )

        if len(filesArray) == 0:
            return Response("Not found!", status=status.HTTP_404_NOT_FOUND)
        
        # compress each file and put them in the same zip file, all in memory
        zipFile = BytesIO()
        with zipfile.ZipFile(zipFile, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in filesArray:
                zf.writestr(f[0], f[1].read())
        zipFile.seek(0) # reset zip file

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},downloaded,{Logging.Object.OBJECT},files as zip," + str(datetime.now()))        
        return createFileResponse(zipFile, filename=processID+".zip")
    except (Exception) as error:
        message = f"Error while downloading files as zip: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        
        
#########Serializer#############
#TODO Add serializer  
# "deleteFile": ("public/deleteFile/", miscellaneous.deleteFile),
#######################################################
@extend_schema(
    summary="Delete a file from storage",
    description=" ",
    tags=['files'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@api_view(["DELETE"])
def deleteFile(request, projectID, processID, fileID):
    """
    Delete a file from storage

    :param request: Request of user for a specific file of a process
    :type request: HTTP DELETE
    :param projectID: Project ID
    :type projectID: str
    :param processID: process ID
    :type processID: Str
    :param fileID: file ID
    :type fileID: Str
    :return: Successful or not
    :rtype: HTTPResponse

    """
    try:

        # Retrieve the files infos from either the session or the database
        fileOfThisProcess, flag = getFilesInfoFromProcess(request, projectID, processID, fileID)

        deletions = {"changes": {}, "deletions": {}}
        deletions["deletions"][ProcessUpdates.files] = {fileOfThisProcess[FileObjectContent.id]: fileOfThisProcess}
        
        # TODO send deletion to service, should the deleted file be the model for example
        message, flag = PPManagement.updateProcessFunction(request, deletions, projectID, [processID])
        if flag is False:
            return Response("Not logged in", status=status.HTTP_401_UNAUTHORIZED)
        if isinstance(message, Exception):
            raise message

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},file {fileID}," + str(datetime.now()))        
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error while detelting files: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
#########Serializer#############
#TODO Add serializer  
# "downloadProcessHistory": ("public/downloadProcessHistory/", miscellaneous.downloadProcessHistory),
#######################################################
@extend_schema(
    summary="See who has done what and when and download this as pdf",
    description=" ",
    tags=['files'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=False)
@checkIfUserMaySeeProcess(json=False)
@api_view(["GET"])
def downloadProcessHistory(request, processID):
    """
    See who has done what and when and download this as pdf

    :param request: GET Request
    :type request: HTTP GET
    :param processID: The process of interest
    :type processID: str
    :return: PDF of process history
    :rtype: Fileresponse

    """
    try:
        # get Project
        processObj = pgProcesses.ProcessManagementBase.getProcessObj("",processID)
        if processObj == None:
            raise Exception("Process not found in DB!")

        # gather interesting info
        listOfData = pgProcesses.ProcessManagementBase.getData(processID, processObj)
        
        fontsize = 12.0
        maxEntriesPerPage = math.floor(pagesizes.A4[1]/fontsize) -1
        numberOfPages = math.ceil(len(listOfData)/(pagesizes.A4[1]/fontsize))

        # create file like object
        outPDFBuffer = BytesIO()
        outPDF = canvas.Canvas(outPDFBuffer, pagesize=pagesizes.A4, bottomup=1, initialFontSize=fontsize)
        
        # make pretty
        defaultY = pagesizes.A4[1]-fontsize
        x = 0
        y = defaultY
        pageNumber = 1
        # first line
        outPDF.drawString(x,y,"Index,CreatedBy,CreatedWhen,Type,Content")
        y -= fontsize
        for idx, entry in enumerate(listOfData):
            if idx >= maxEntriesPerPage*pageNumber:
                # render pdf page
                outPDF.showPage()
                pageNumber += 1
                y = defaultY
                outPDF.drawString(x,y,"Index,CreatedBy,CreatedWhen,Type,Content")
                y -= fontsize
            createdBy = pgProfiles.ProfileManagementBase.getUserNameViaHash(entry[DataDescription.createdBy])
            createdWhen = timezone.make_aware(datetime.strptime(entry[DataDescription.createdWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')).strftime("%Y-%m-%d %H:%M:%S")
            typeOfData = dataTypeToString(entry[DataDescription.type])
            dataContent = entry[DataDescription.data]
            if entry[DataDescription.type] == DataType.FILE:
                dataContent = entry[DataDescription.data][FileObjectContent.fileName]
            outString = f"{idx},{createdBy},{createdWhen},{typeOfData},{dataContent}"
            outPDF.drawString(x,y,outString)
            y -= fontsize


        # save pdf
        outPDF.showPage()
        outPDF.save()
        outPDFBuffer.seek(0)

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},downloaded,{Logging.Object.OBJECT},history as pdf," + str(datetime.now()))

        # return file
        return createFileResponse(outPDFBuffer, filename=processID+".pdf")
    except (Exception) as error:
        message = f"Error in downloadProcessHistory: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        
        
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


#########Serializer#############
#TODO Add serializer  
# "statusButtonRequest": ("public/statusButtonRequest/", miscellaneous.statusButtonRequest),
#######################################################
@extend_schema(
    summary="Button was clicked, so the state must change (transition inside state machine)",
    description=" ",
    tags=['public'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)

@api_view(["GET"])
def statusButtonRequest(request):
    """
    Button was clicked, so the state must change (transition inside state machine)
    
    :param request: POST Request
    :type request: HTTP POST
    :return: Response with new buttons
    :rtype: JSONResponse
    """
    try:
        # get from info, create correct object, initialize statemachine, switch state accordingly
        info = json.loads(request.body.decode("utf-8"))
        projectID = info[InterfaceForStateChange.projectID]
        processIDs = info[InterfaceForStateChange.processIDs]
        buttonData = info[InterfaceForStateChange.buttonData]
        if "deleteProcess" in buttonData[InterfaceForStateChange.type]:
            retVal = deleteProcessFunction(request.session, processIDs)
            if isinstance(retVal, Exception):
                raise retVal
            return retVal
        elif "cloneProcess" in buttonData[InterfaceForStateChange.type]:
            retVal = cloneProcess(request, projectID, processIDs)
            if isinstance(retVal, Exception):
                raise retVal
            return retVal
        else:
            nextState = buttonData[InterfaceForStateChange.targetStatus]

            contentManager = ManageContent(request.session)
            interface = contentManager.getCorrectInterface(statusButtonRequest.cls.__name__)
            for processID in processIDs:
                process = interface.getProcessObj(projectID, processID)
                sm = StateMachine(initialAsInt=process.processStatus)
                sm.onButtonEvent(nextState, interface, process)

        return JsonResponse({})
    except (Exception) as error:
        message = f"Error in statusButtonRequest: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)