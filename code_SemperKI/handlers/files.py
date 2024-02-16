"""
Part of Semper-KI software

Silvio Weging 2023

Contains: File upload handling
"""

import logging, zipfile
from io import BytesIO
from datetime import datetime
import math

from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes

from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities.basics import Logging, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient, checkIfUserIsLoggedIn, checkIfRightsAreSufficient
from Generic_Backend.code_General.utilities.files import createFileResponse
from Generic_Backend.code_General.definitions import FileObjectContent
from Generic_Backend.code_General.connections import s3

from .projectAndProcessManagement import updateProcessFunction, getProcessAndProjectFromSession

from ..connections.content.postgresql import pgProcesses
from ..definitions import ProcessUpdates, DataType, ProcessDescription, DataDescription, dataTypeToString
from ..utilities.basics import checkIfUserMaySeeProcess, manualCheckIfUserMaySeeProcess

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")


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
            returnVal = s3.manageLocalS3.uploadFile(filePath, request.FILES.getlist(fileName)[0])
            if returnVal is not True:
                return HttpResponse("Failed", status=500)
        
        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False:
            return HttpResponse("Unsufficient rights!", status=401)
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
        # Retrieve the files infos from either the session or the database
        fileOfThisProcess = {}
        currentProjectID, currentProcess = getProcessAndProjectFromSession(request.session,processID)
        if currentProcess != None:
            if fileID in currentProcess[ProcessDescription.files]:
                fileOfThisProcess = currentProcess[ProcessDescription.files][fileID]
            else:
                return HttpResponse("Not found!", status=404)
        else:
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, downloadFile.__name__):
                userID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
                if manualCheckIfUserMaySeeProcess(request.session, userID, processID):
                    currentProcess = pgProcesses.ProcessManagementBase.getProcessObj(processID)
                    fileOfThisProcess = currentProcess.files[fileID]
                    if len(fileOfThisProcess) == 0:
                        return HttpResponse("Not found!", status=404)
                else:
                    return HttpResponse("Not allowed to see process!", status=401)
            else:
                return HttpResponse("Not logged in or rights insufficient!", status=401)

        # retrieve the correct file and download it from aws to the user
        content, Flag = s3.manageLocalS3.downloadFile(fileOfThisProcess[FileObjectContent.path])
        if Flag is False:
            content, Flag = s3.manageRemoteS3.downloadFile(fileOfThisProcess[FileObjectContent.path])
            if Flag is False:
                return HttpResponse("Not found!", status=404)
            
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.FETCHED},downloaded,{Logging.Object.OBJECT},file {fileOfThisProcess[FileObjectContent.fileName]}," + str(datetime.now()))
            
        return createFileResponse(content, filename=fileOfThisProcess[FileObjectContent.fileName])

    except (Exception) as error:
        loggerError.error(f"Error while downloading file: {str(error)}")
        return HttpResponse("Failed", status=500)

#######################################################
@require_http_methods(["GET"])
def downloadFilesAsZip(request, processID):
    """
    Send files to user as zip

    :param request: Request of user for all selected files of a process
    :type request: HTTP POST
    :param processID: process ID
    :type processID: Str
    :return: Saved content
    :rtype: FileResponse

    """
    try:
        fileIDs = request.GET['fileIDs'].split(",")
        filesArray = []

        # Retrieve the files infos from either the session or the database
        filesOfThisProcess = {}
        currentProjectID, currentProcess = getProcessAndProjectFromSession(request.session,processID)
        if currentProcess != None:
            filesOfThisProcess = currentProcess[ProcessDescription.files]
        else:
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, downloadFile.__name__):
                userID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
                if manualCheckIfUserMaySeeProcess(request.session, userID, processID):
                    currentProcess = pgProcesses.ProcessManagementBase.getProcessObj(processID)
                    filesOfThisProcess = currentProcess.files
                else:
                    return HttpResponse("Not allowed to see process!", status=401)
            else:
                return HttpResponse("Not logged in or rights insufficient!", status=401)

        # get files, download them from aws, put them in an array together with their name
        for elem in filesOfThisProcess:
            currentEntry = filesOfThisProcess[elem]
            if FileObjectContent.id in currentEntry and currentEntry[FileObjectContent.id] in fileIDs:
                content, Flag = s3.manageLocalS3.downloadFile(currentEntry[FileObjectContent.path])
                if Flag is False:
                    content, Flag = s3.manageRemoteS3.downloadFile(currentEntry[FileObjectContent.path])
                    if Flag is False:
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
        processObj = pgProcesses.ProcessManagementBase.getProcessObj(processID)
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
def deleteFile(request, processID, fileID):
    """
    Delete a file from storage

    :param request: Request of user for a specific file of a process
    :type request: HTTP DELETE
    :param processID: process ID
    :type processID: Str
    :param fileID: file ID
    :type fileID: Str
    :return: Successful or not
    :rtype: HTTPResponse

    """
    try:

        # Retrieve the files infos from either the session or the database
        fileOfThisProcess = {}
        liesInDatabase = False
        currentProjectID, currentProcess = getProcessAndProjectFromSession(request.session,processID)
        if currentProcess != None:
            if fileID in currentProcess[ProcessDescription.files]:
                fileOfThisProcess = currentProcess[ProcessDescription.files][fileID]
            else:
                return HttpResponse("Not found!", status=404)
        else:
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, deleteFile.__name__):
                userID = pgProfiles.ProfileManagementBase.getUserHashID(request.session)
                if manualCheckIfUserMaySeeProcess(request.session, userID, processID):
                    currentProcess = pgProcesses.ProcessManagementBase.getProcessObj(processID)
                    fileOfThisProcess = currentProcess.files[fileID]
                    if len(fileOfThisProcess) == 0:
                        return HttpResponse("Not found!", status=404)                
                    liesInDatabase = True
                else:
                    return HttpResponse("Not allowed to see process!", status=401)
            else:
                return HttpResponse("Not logged in or rights insufficient!", status=401)
        
        deletions = {"changes": {}, "deletions": {}}
        deletions["deletions"][ProcessUpdates.files] = {fileOfThisProcess[FileObjectContent.id]: fileOfThisProcess}
        
        # TODO send deletion to service, should the deleted file be the model for example
        
        message, flag = updateProcessFunction(request, deletions, currentProjectID, [processID])
        if flag is False:
            return HttpResponse("Not logged in", status=401)
        if isinstance(message, Exception):
            raise message
        
        if not liesInDatabase: # file deletion in database already triggers file deletion in aws
            returnVal = s3.manageLocalS3.deleteFile(fileOfThisProcess[FileObjectContent.path])
            if returnVal is not True:
                raise Exception("Deletion of file" + fileID + " failed")

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},file {fileID}," + str(datetime.now()))        
        return HttpResponse("Success", status=200)
    except (Exception) as error:
        loggerError.error(f"Error while deleting file: {str(error)}")
        return HttpResponse("Failed", status=500)
