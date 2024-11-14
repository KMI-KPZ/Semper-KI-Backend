"""
Part of Semper-KI software

Silvio Weging 2023

Contains: File upload handling
"""
import base64
import logging, zipfile
import os
from logging import getLogger
from io import BytesIO
from datetime import datetime
import math

from boto3.s3.transfer import TransferConfig
from botocore.response import StreamingBody
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes

from django.http import HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from rest_framework import status, serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities.basics import checkVersion, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient, checkIfUserIsLoggedIn, checkIfRightsAreSufficient
from Generic_Backend.code_General.utilities.crypto import EncryptionAdapter
from Generic_Backend.code_General.utilities.files import createFileResponse
from Generic_Backend.code_General.definitions import FileObjectContent, Logging, FileTypes
from Generic_Backend.code_General.connections import s3

from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.handlers.public.process import updateProcessFunction
import code_SemperKI.connections.content.manageContent as ManageC
from ...connections.content.postgresql import pgProcesses
from ...definitions import ProcessUpdates, DataType, ProcessDescription, DataDescription, dataTypeToString
from ...utilities.basics import checkIfUserMaySeeProcess, manualCheckIfUserMaySeeProcess, testPicture
from django.http.request import HttpRequest

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
loggerInfo = logging.getLogger("info")
loggerDebug = getLogger("django_debug")
#######################################################

############################################################
# Helper function
############################################################
# def getProcessAndProjectFromSession(session, processID):
#     """
#     Retrieve a specific process from the current session instead of the database
    
#     :param session: Session of the current user
#     :type session: Dict
#     :param projectID: Process ID
#     :type projectID: Str
#     :return: Process or None
#     :rtype: Dict or None
#     """
#     try:
#         contentManager = ManageC.ManageContent(session)
#         if contentManager.sessionManagement.getIfContentIsInSession():
#             return contentManager.sessionManagement.structuredSessionObj.getProcessAndProjectPerID(processID)
#         else:
#             return (None, None)
#     except (Exception) as error:
#         loggerError.error(f"getProcessAndProjectFromSession: {str(error)}")
#         return (None, None)

#########################################################################
# uploadFiles
#"uploadFiles": ("public/uploadFiles/",files.uploadFiles)
#########################################################################
#TODO Add serializer for uploadFiles
#######################################################
class SReqUploadFiles(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    processID = serializers.CharField(max_length=200)
    origin = serializers.CharField(max_length=200)
    file = serializers.FileField(required=False)
#########################################################################
# Handler    
@extend_schema(
     summary="File upload for a process",
     description=" ",
     request={
        "multipart/form-data": SReqUploadFiles
    },	
     tags=['FE - Files'],
     responses={
         200: None,
         401: ExceptionSerializer,
         500: ExceptionSerializer
     }
 )
@api_view(["POST"])
@checkVersion(0.3)
def uploadFiles(request:Request):
    """
    File upload for a process

    :param request: Request with files in it
    :type request: HTTP POST
    :return: Successful or not
    :rtype: HTTP Response
    """
    try:
        inSerializer = SReqUploadFiles(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {uploadFiles.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        info = inSerializer.data
        projectID = info["projectID"]
        processID = info["processID"]
        origin = info["origin"]
        assert projectID != "", f"In {uploadFiles.cls.__name__}: non-empty projectID expected"
        assert processID != "", f"In {uploadFiles.cls.__name__}: non-empty processID expected"
        assert origin != "", f"In {uploadFiles.cls.__name__}: non-empty origin expected"


        content = ManageC.ManageContent(request.session)
        interface = content.getCorrectInterface(uploadFiles.cls.__name__)
        if interface == None:
            message = f"Rights not sufficient in {uploadFiles.cls.__name__}"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        if interface.checkIfFilesAreRemote(projectID, processID):
            remote = True
        else:
            remote = False

        fileNames = list(request.FILES.keys())
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
        assert userName != "", f"In {uploadFiles.cls.__name__}: non-empty userName expected"
        changes = {"changes": {ProcessUpdates.files: {}}}

        # check if duplicates exist
        existingFileNames = set()
        processContent = interface.getProcess(projectID, processID)
        if isinstance(processContent, Exception):
            message = f"Process not found in {uploadFiles.cls.__name__}"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        for key in processContent[ProcessDescription.files]:
            value = processContent[ProcessDescription.files][key]
            existingFileNames.add(value[FileObjectContent.fileName])

        for fileName in fileNames:
            assert fileName != "", f"In {uploadFiles.cls.__name__}: non-empty fileName expected"
            # rename duplicates
            counterForFileName = 1
            nameOfFile = fileName
            while nameOfFile in existingFileNames:
                fileNameRoot, extension= os.path.splitext(nameOfFile)
                if counterForFileName > 100000:
                    raise Exception("Too many files with the same name uploaded!")
                
                if "_" in fileNameRoot:
                    fileNameRootSplit = fileNameRoot.split("_")
                    try:
                        counterForFileName = int(fileNameRootSplit[-1])
                        fileNameRoot = "_".join(fileNameRootSplit[:-1])
                        counterForFileName += 1
                    except:
                        pass
                nameOfFile = fileNameRoot + "_" + str(counterForFileName) + extension
                counterForFileName += 1

            for file in request.FILES.getlist(fileName):
                fileID = crypto.generateURLFriendlyRandomString()
                filePath = projectID + "/" + processID + "/" + fileID
                changes["changes"][ProcessUpdates.files][fileID] = {}
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.id] = fileID
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.path] = filePath
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.fileName] = nameOfFile
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.imgPath] = testPicture
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.date] = str(timezone.now())
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.createdBy] = userName
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.createdByID] = content.getClient()
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.size] = file.size
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.type] = FileTypes.File
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.origin] = origin
                if remote:
                    changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.remote] = True
                    returnVal = s3.manageRemoteS3.uploadFile(filePath, file)
                    if returnVal is not True:
                        return Response("Failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.remote] = False
                    returnVal = s3.manageLocalS3.uploadFile(filePath, file)
                    if returnVal is not True:
                        return Response("Failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
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
    
#######################################################
# @require_http_methods(["GET"])
# def downloadFile(request:Request, processID, fileID):
#     """
#     Send file to user from storage
#     DEPRECATED!!!!

#     :param request: Request of user for a specific file of a process
#     :type request: HTTP POST
#     :param processID: process ID
#     :type processID: Str
#     :param fileID: file ID
#     :type fileID: Str
#     :return: Saved content
#     :rtype: FileResponse

#     """
#     try:
#         # Retrieve the files info from either the session or the database
#         fileOfThisProcess = {}
#         currentProjectID, currentProcess = getProcessAndProjectFromSession(request.session,processID)
#         if currentProcess != None:
#             if fileID in currentProcess[ProcessDescription.files]:
#                 fileOfThisProcess = currentProcess[ProcessDescription.files][fileID]
#             else:
#                 return HttpResponse("Not found!", status=404)
#         else:
#             if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, downloadFile.__name__):
#                 userID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
#                 if manualCheckIfUserMaySeeProcess(request.session, userID, processID):
#                     currentProcess = pgProcesses.ProcessManagementBase.getProcessObj("",processID)
#                     fileOfThisProcess = currentProcess.files[fileID]
#                     if len(fileOfThisProcess) == 0:
#                         return HttpResponse("Not found!", status=404)
#                 else:
#                     return HttpResponse("Not allowed to see process!", status=401)
#             else:
#                 return HttpResponse("Not logged in or rights insufficient!", status=401)

#         # retrieve the correct file and download it from aws to the user
#         content, flag = s3.manageLocalS3.downloadFile(fileOfThisProcess[FileObjectContent.path])
#         if flag is False:
#             content, flag = s3.manageRemoteS3.downloadFile(fileOfThisProcess[FileObjectContent.path])
#             if flag is False:
#                 return HttpResponse("Not found!", status=404)
            
#         logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},downloaded,{Logging.Object.OBJECT},file {fileOfThisProcess[FileObjectContent.fileName]}," + str(datetime.now()))
            
#         return createFileResponse(content, filename=fileOfThisProcess[FileObjectContent.fileName])

#     except (Exception) as error:
#         loggerError.error(f"Error while downloading file: {str(error)}")
#         return HttpResponse("Failed", status=500)


#######################################################
def getFilesInfoFromProcess(request: HttpRequest, projectID: str, processID: str, fileID: str="") -> tuple[object, bool]:
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
            return (HttpResponse("Not logged in or rights insufficient!", status=401),False)
        
        if not contentManager.checkRightsForProcess(processID):
            return (HttpResponse("Not allowed to see process!", status=401),False)

        currentProcess = interface.getProcessObj(projectID, processID)
        if currentProcess == None:
            return (HttpResponse("Not found!", status=404), False)
        
        if fileID != "":
            if fileID not in currentProcess.files:
                return (HttpResponse("Not found!", status=404),False)
            
            fileOfThisProcess = currentProcess.files[fileID]

            if contentManager.getClient() != fileOfThisProcess[FileObjectContent.createdByID]:
                return (HttpResponse("Not allowed to access file!", status=401), False)

            return (fileOfThisProcess, True)
        else:
            return (currentProcess.files, True)

    except (Exception) as error:
        loggerError.error(f"Error while retrieving file information: {str(error)}")
        return (HttpResponse("Failed", status=500),False)


#######################################################
def getFileObject(request: HttpRequest, projectID: str, processID: str, fileID: str) -> tuple[object, bool, bool]:
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


#######################################################
def getFileReadableStream(request:Request, projectID, processID, fileID) -> tuple[EncryptionAdapter, bool]:
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


#######################################################
def moveFileToRemote(fileKeyLocal, fileKeyRemote, deleteLocal = True, printDebugInfo = False) -> bool:
    """
    Move a file from local to remote storage with on the fly encryption not managing other information

    :param fileKeyLocal: The key with which to retrieve the file again later
    :type fileKeyLocal: Str
    :param fileKeyRemote: The key with which to retrieve the file again later
    :type fileKeyRemote: Str
    :param delteLocal: If set to True the local file will be deleted after the transfer
    :type delteLocal: bool
    :return: Success or error
    :rtype: Bool or Error

    """
    try:
        # try to retrieve it from local storage
        fileStreamingBody, flag = s3.manageLocalS3.getFileStreamingBody(fileKeyLocal)
        if flag is False:
            logger.warning(f"File {fileKeyLocal} not found in local storage to move to remote")
            return False

        config = TransferConfig(
            multipart_threshold=1024 * 1024 * 5,  # Upload files larger than 5 MB in multiple parts (default: 8 MB)
            max_concurrency=10,  # Use 10 threads for large files (default: 10, max 10)
            multipart_chunksize=1024 * 1024 * 5,  # 5 MB parts (min / default: 5 MB)
            use_threads=True  # allow threads for multipart upload
        )

        #setup encryption
        encryptionAdapter = EncryptionAdapter(fileStreamingBody)
        encryptionAdapter.setupEncryptOnRead(base64.b64decode(s3.manageRemoteS3.aesEncryptionKey))
        if printDebugInfo:
            encryptionAdapter.setDebugLogger(loggerDebug)
        try :
            result = s3.manageRemoteS3.uploadFileObject(fileKeyRemote, encryptionAdapter, config)
            #TODO check if the file was uploaded successfully
        except Exception as e:
            logging.error(f"Error while uploading file {fileKeyLocal} from local to remote {fileKeyRemote}: {str(e)}")
            return False

        if deleteLocal:
            returnVal = s3.manageLocalS3.deleteFile(fileKeyLocal)
            if returnVal is not True:
                logging.error("Deletion of file" + fileKeyLocal + " failed")

        return True

    except Exception as error:
        loggerError.error(f"Error while moving file to remote: {str(error)}")
        return False

#########################################################################
# downloadFileStream
#"downloadFile": ("public/downloadFile/<str:projectID>/<str:processID>/<str:fileID>/", files.downloadFileStream)
#########################################################################
#TODO Add serializer for downloadFileStream
#########################################################################
# Handler     
@extend_schema(
    summary="Send file to user from storage",
    description="Send file to user from storage with request of user for a specific file of a process  ",
    tags=["FE - Files"],
    request=None,
    responses={
        200: None,
        500: ExceptionSerializer
    }
)
@api_view(["GET"])
@checkVersion(0.3)
def downloadFileStream(request:Request, projectID, processID, fileID):
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

#########################################################################
# downloadFilesAsZip
#"downloadFilesAsZip": ("public/downloadFilesAsZip/<str:projectID>/<str:processID>/",files.downloadFilesAsZip)
#########################################################################
#TODO Add serializer for downloadFilesAsZip
#########################################################################
# Handler    
@extend_schema(
    summary="Send files to user as zip",
    description=" ",
    tags=["FE - Files"],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        404: ExceptionSerializer,
        500: ExceptionSerializer,
    }
)
@api_view(["GET"])
@checkVersion(0.3)
def downloadFilesAsZip(request:Request, projectID, processID):
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
                if FileObjectContent.isFile not in currentEntry or currentEntry[FileObjectContent.isFile]:
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
        
#########################################################################
# downloadProcessHistory
#"downloadProcessHistory": ("public/downloadProcessHistory/<str:processID>/", files.downloadProcessHistory)
#########################################################################
#TODO Add serializer for downloadProcessHistory
#########################################################################
# Handler  
@extend_schema(
    summary="See who has done what and when and download this as pdf",
    description=" ",
    tags=['FE - Files'],
    request=None,
    responses={
        200: None,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=False)
@checkIfUserMaySeeProcess(json=False)
@api_view(["GET"])
@checkVersion(0.3)
def downloadProcessHistory(request:Request, processID):
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

#########################################################################
# deleteFile
#"deleteFile": ("public/deleteFile/<str:projectID>/<str:processID>/<str:fileID>/",files.deleteFile)
#########################################################################
#TODO Add serializer for deleteFile
#########################################################################
# Handler  
@extend_schema(
    summary="Delete a file from storage",
    description=" ",
    tags=['FE - Files'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["DELETE"])
@checkVersion(0.3)
def deleteFile(request:Request, projectID, processID, fileID):
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
        fileOfThisProcess, flag = getFilesInfoFromProcess(request._request, projectID, processID, fileID)
        if flag == False:
            return fileOfThisProcess # Response if something went wrong

        deletions = {"changes": {}, "deletions": {}}
        deletions["deletions"][ProcessUpdates.files] = {fileOfThisProcess[FileObjectContent.id]: fileOfThisProcess}
        
        # TODO send deletion to service, should the deleted file be the model for example
        message, flag = updateProcessFunction(request, deletions, projectID, [processID])
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
