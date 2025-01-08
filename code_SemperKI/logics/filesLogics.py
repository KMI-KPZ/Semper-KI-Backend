"""
Part of Semper-KI software

Silvio Weging 2025

Contains: File upload handling logics
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

from django.utils import timezone
from django.http import HttpResponse

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities.crypto import EncryptionAdapter
from Generic_Backend.code_General.utilities.files import createFileResponse
from Generic_Backend.code_General.definitions import FileObjectContent, Logging, FileTypes
from Generic_Backend.code_General.connections import s3

from code_SemperKI.logics.processLogics import updateProcessFunction
import code_SemperKI.connections.content.manageContent as ManageC
from ..connections.content.postgresql import pgProcesses
from ..definitions import ProcessUpdates, DataType, ProcessDescription, DataDescription, dataTypeToString
from ..utilities.basics import testPicture
from django.http.request import HttpRequest

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
loggerInfo = logging.getLogger("info")
loggerDebug = getLogger("django_debug")
#######################################################

#######################################################
def logicForUploadFiles(request, validatedInput:dict, functionName:str):
    """
    Logics for uploading files

    :param request: HttpRequest
    :type request: HttpRequest
    :param validatedInput: The input
    :type validatedInput: dict
    :param functionName: name of the handler
    :type functionName: str
    :return: Nothing or Exception
    :rtype: None|Exception, int
    
    """
    try:
        projectID = validatedInput["projectID"]
        processID = validatedInput["processID"]
        origin = validatedInput["origin"]
        assert projectID != "", f"In {functionName}: non-empty projectID expected"
        assert processID != "", f"In {functionName}: non-empty processID expected"
        assert origin != "", f"In {functionName}: non-empty origin expected"


        content = ManageC.ManageContent(request.session)
        interface = content.getCorrectInterface(functionName)
        if interface == None:
            return Exception(f"Rights not sufficient in {functionName}"), status.HTTP_401_UNAUTHORIZED

        if interface.checkIfFilesAreRemote(projectID, processID):
            remote = True
        else:
            remote = False

        fileNames = list(request.FILES.keys())
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
        assert userName != "", f"In {functionName}: non-empty userName expected"
        changes = {"changes": {ProcessUpdates.files: {}}}

        # check if duplicates exist
        existingFileNames = set()
        processContent = interface.getProcess(projectID, processID)
        if isinstance(processContent, Exception):
            return Exception(f"Process not found in {functionName}"), status.HTTP_404_NOT_FOUND

        for key in processContent[ProcessDescription.files]:
            value = processContent[ProcessDescription.files][key]
            existingFileNames.add(value[FileObjectContent.fileName])

        for fileName in fileNames:
            assert fileName != "", f"In {functionName}: non-empty fileName expected"
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
            return Exception("Insufficient rights!"), status.HTTP_401_UNAUTHORIZED
        if isinstance(message, Exception):
            raise message

        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},files,"+str(datetime.now()))
        return None, status.HTTP_200_OK
    except Exception as e:
        logger.error(f"Error in {functionName}: {str(e)}")
        return e, status.HTTP_500_INTERNAL_SERVER_ERROR
    
#######################################################

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
        interface = contentManager.getCorrectInterface("downloadFileStream")
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

#######################################################
def logicForDownloadAsZip(request:Request, projectID:str, processID:str, functionName:str):
    """
    Logics for downloading files as a zip file

    :param request: HttpRequest
    :type request: HttpRequest
    :param projectID: Project ID
    :type projectID: str
    :param processID: Process ID
    :type processID: str
    :param functionName: name of the handler
    :type functionName: str
    :return: HttpResponse
    :rtype: HttpResponse
    
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
    except Exception as e:
        logger.error(f"Error in {functionName}: {str(e)}")
        return Response("Failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#######################################################
def logicForDownloadProcessHistory(request:Request, processID:str, functionName:str):
    """
    Logics for downloading the history of a process

    :param request: HttpRequest
    :type request: HttpRequest
    :param processID: Process ID
    :type processID: str
    :param functionName: name of the handler
    :type functionName: str
    :return: HttpResponse
    :rtype: HttpResponse
    
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
    except Exception as e:
        logger.error(f"Error in {functionName}: {str(e)}")
        return Response("Failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#######################################################
def logicForDeleteFile(request:Request, projectID:str, processID:str, fileID:str, functionName:str):
    """
    Logics for deleting a file

    :param request: HttpRequest
    :type request: HttpRequest
    :param projectID: Project ID
    :type projectID: str
    :param processID: Process ID
    :type processID: str
    :param fileID: File ID
    :type fileID: str
    :param functionName: name of the handler
    :type functionName: str
    :return: None or Exception, statusCode
    :rtype: None|Exception, int

    """
    try:
        # Retrieve the files infos from either the session or the database
        fileOfThisProcess, flag = getFilesInfoFromProcess(request._request, projectID, processID, fileID)
        if flag == False:
            return Exception(str(fileOfThisProcess.content)), fileOfThisProcess.status_code # Response if something went wrong

        deletions = {"changes": {}, "deletions": {}}
        deletions["deletions"][ProcessUpdates.files] = {fileOfThisProcess[FileObjectContent.id]: fileOfThisProcess}
        
        
        message, flag = updateProcessFunction(request, deletions, projectID, [processID])
        if flag is False:
            return Exception("Not logged in"), status.HTTP_401_UNAUTHORIZED
        if isinstance(message, Exception):
            raise message

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},file {fileID}," + str(datetime.now()))        
        return None, status.HTTP_200_OK
    except Exception as e:
        logger.error(f"Error in {functionName}: {str(e)}")
        return e, status.HTTP_500_INTERNAL_SERVER_ERROR