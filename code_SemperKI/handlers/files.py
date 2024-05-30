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

from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient, checkIfUserIsLoggedIn, checkIfRightsAreSufficient
from Generic_Backend.code_General.utilities.crypto import EncryptionAdapter
from Generic_Backend.code_General.utilities.files import createFileResponse
from Generic_Backend.code_General.definitions import FileObjectContent, Logging
from Generic_Backend.code_General.connections import s3

import code_SemperKI.handlers.projectAndProcessManagement as PPManagement
import code_SemperKI.connections.content.manageContent as ManageC
from ..connections.content.postgresql import pgProcesses
from ..definitions import ProcessUpdates, DataType, ProcessDescription, DataDescription, dataTypeToString
from ..utilities.basics import checkIfUserMaySeeProcess, manualCheckIfUserMaySeeProcess
from django.http.request import HttpRequest

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
loggerInfo = logging.getLogger("info")
loggerDebug = getLogger("django_debug")

#######################################################
@require_http_methods(["POST"])
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
        interface = content.getCorrectInterface(uploadFiles.__name__)
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
                    return HttpResponse("Failed", status=500)
            else:
                changes["changes"][ProcessUpdates.files][fileID][FileObjectContent.remote] = False
                returnVal = s3.manageLocalS3.uploadFile(filePath, request.FILES.getlist(fileName)[0])
                if returnVal is not True:
                    return HttpResponse("Failed", status=500)
        
        # Save into files field of the process
        message, flag = PPManagement.updateProcessFunction(request, changes, projectID, [processID])
        if flag is False:
            return HttpResponse("Insufficient rights!", status=401)
        if isinstance(message, Exception):
            raise message

        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},files,"+str(datetime.now()))
        return HttpResponse("Success")
    except (Exception) as error:
        loggerError.error(f"Error while uploading files: {str(error)}")
        return HttpResponse("Failed", status=500)
    
#######################################################
@require_http_methods(["GET"])
def downloadFile(request, processID, fileID):
    """
    Send file to user from storage
    DEPRECATED!!!!

    :param request: Request of user for a specific file of a process
    :type request: HTTP POST
    :param processID: process ID
    :type processID: Str
    :param fileID: file ID
    :type fileID: Str
    :return: Saved content
    :rtype: FileResponse

    """
    try:
        # Retrieve the files info from either the session or the database
        fileOfThisProcess = {}
        currentProjectID, currentProcess = PPManagement.getProcessAndProjectFromSession(request.session,processID)
        if currentProcess != None:
            if fileID in currentProcess[ProcessDescription.files]:
                fileOfThisProcess = currentProcess[ProcessDescription.files][fileID]
            else:
                return HttpResponse("Not found!", status=404)
        else:
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, downloadFile.__name__):
                userID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
                if manualCheckIfUserMaySeeProcess(request.session, userID, processID):
                    currentProcess = pgProcesses.ProcessManagementBase.getProcessObj("",processID)
                    fileOfThisProcess = currentProcess.files[fileID]
                    if len(fileOfThisProcess) == 0:
                        return HttpResponse("Not found!", status=404)
                else:
                    return HttpResponse("Not allowed to see process!", status=401)
            else:
                return HttpResponse("Not logged in or rights insufficient!", status=401)

        # retrieve the correct file and download it from aws to the user
        content, flag = s3.manageLocalS3.downloadFile(fileOfThisProcess[FileObjectContent.path])
        if flag is False:
            content, flag = s3.manageRemoteS3.downloadFile(fileOfThisProcess[FileObjectContent.path])
            if flag is False:
                return HttpResponse("Not found!", status=404)
            
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},downloaded,{Logging.Object.OBJECT},file {fileOfThisProcess[FileObjectContent.fileName]}," + str(datetime.now()))
            
        return createFileResponse(content, filename=fileOfThisProcess[FileObjectContent.fileName])

    except (Exception) as error:
        loggerError.error(f"Error while downloading file: {str(error)}")
        return HttpResponse("Failed", status=500)


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
        interface = contentManager.getCorrectInterface(downloadFile.__name__)
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


#######################################################
@require_http_methods(["GET"])
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
            return HttpResponse("Failed", status=500)

        if os.getenv("DJANGO_LOG_LEVEL", None) == "DEBUG":
            encryptionAdapter.setDebugLogger(loggerDebug)

        return createFileResponse(encryptionAdapter, filename=fileMetaData[FileObjectContent.fileName])

    except (Exception) as error:
        loggerError.error(f"Error while downloading file: {str(error)}")
        return HttpResponse("Failed", status=500)



#######################################################
@require_http_methods(["GET"])
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
                        return HttpResponse("Not found!", status=404)
                
                filesArray.append( (currentEntry[FileObjectContent.fileName], content) )

        if len(filesArray) == 0:
            return HttpResponse("Not found!", status=404)
        
        # compress each file and put them in the same zip file, all in memory
        zipFile = BytesIO()
        with zipfile.ZipFile(zipFile, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in filesArray:
                zf.writestr(f[0], f[1].read())
        zipFile.seek(0) # reset zip file

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},downloaded,{Logging.Object.OBJECT},files as zip," + str(datetime.now()))        
        return createFileResponse(zipFile, filename=processID+".zip")

    except (Exception) as error:
        loggerError.error(f"Error while downloading files as zip: {str(error)}")
        return HttpResponse("Failed", status=500)

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"]) 
@checkIfRightsAreSufficient(json=False)
@checkIfUserMaySeeProcess(json=False)
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
        loggerError.error(f"viewProcessHistory: {str(error)}")
        return HttpResponse("Error!", status=500)


#######################################################
@require_http_methods(["DELETE"])
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
            return HttpResponse("Not logged in", status=401)
        if isinstance(message, Exception):
            raise message

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},file {fileID}," + str(datetime.now()))        
        return HttpResponse("Success", status=200)
    except (Exception) as error:
        loggerError.error(f"Error while deleting file: {str(error)}")
        return HttpResponse("Failed", status=500)
