"""
Part of Semper-KI software

Silvio Weging 2023

Contains: handling of model files
"""

import logging
from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.definitions import FileObjectContent
from Generic_Backend.code_General.utilities.basics import Logging, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import ProcessDescription, ProcessUpdates, DataType, DataDescription
from code_SemperKI.handlers.projectAndProcessManagement import updateProcessFunction, getProcessAndProjectFromSession
from code_SemperKI.connections.content.postgresql import pgProcesses
from code_SemperKI.handlers.files import deleteFile

from ..definitions import ServiceDetails
from ..connections.postgresql import pgService

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

#######################################################
@require_http_methods(["POST"])
def uploadModel(request):
    """
    File upload for 3D model

    :param request: request
    :type request: HTTP POST
    :return: Response with information about the file
    :rtype: JSONResponse

    """
    try:
        info = request.POST 
        projectID = info["projectID"]
        processID = info["processID"]
        fileTags = info[FileObjectContent.tags].split(",")
        fileLicenses = info[FileObjectContent.licenses].split(",")
        fileCertificates = info[FileObjectContent.certificates].split(",")

        fileName = list(request.FILES.keys())[0]
        fileID = crypto.generateURLFriendlyRandomString()
        filePath = processID+"/"+fileID
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
        
        model = {fileID: {}}
        model[fileID][FileObjectContent.id] = fileID
        model[fileID][FileObjectContent.fileName] = fileName
        model[fileID][FileObjectContent.tags] = fileTags
        model[fileID][FileObjectContent.date] = str(timezone.now())
        model[fileID][FileObjectContent.licenses] = fileLicenses
        model[fileID][FileObjectContent.certificates] = fileCertificates
        model[fileID][FileObjectContent.URI] = ""
        model[fileID][FileObjectContent.createdBy] = userName
        model[fileID][FileObjectContent.path] = filePath

        returnVal = s3.manageLocalS3.uploadFile(filePath, request.FILES.getlist(fileName)[0])
        if returnVal is not True:
            return JsonResponse({}, status=500)
        
        changes = {"changes": {ProcessUpdates.files: {fileID: model[fileID]}, ProcessUpdates.serviceDetails: {ServiceDetails.model: model[fileID]}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False:
            return JsonResponse({}, status=401)
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},model {fileName},"+str(datetime.now()))
        return JsonResponse(model)
    except (Exception) as error:
        loggerError.error(f"Error while uploading model: {str(error)}")
        return JsonResponse({}, status=500)
    

#######################################################
@require_http_methods(["DELETE"])
def deleteModel(request, processID):
    """
    Delete the model and the file with it, if not done already
    
    :param request: request
    :type request: HTTP POST
    :param processID: process ID
    :type processID: Str
    :return: Successful or not
    :rtype: HTTPResponse

    """
    try:
        modelOfThisProcess = {}
        modelExistsAsFile = False
        currentProjectID, currentProcess = getProcessAndProjectFromSession(request.session,processID)
        if currentProcess != None:
            modelOfThisProcess = currentProcess[ProcessDescription.serviceDetails][ServiceDetails.model]
            if modelOfThisProcess[FileObjectContent.id] in currentProcess[ProcessDescription.files]:
                modelExistsAsFile = True
        else:
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, deleteModel.__name__):
                currentProcess = pgProcesses.ProcessManagementBase.getProcessObj(processID)
                modelOfThisProcess = currentProcess.serviceDetails[ServiceDetails.model]
                if modelOfThisProcess[FileObjectContent.id] in currentProcess.files:
                    modelExistsAsFile = True              
            else:
                return HttpResponse("Not logged in or rights insufficient!", status=401)

        if modelExistsAsFile:
            deleteFile(request, processID, modelOfThisProcess[FileObjectContent.id])
        
        changes = {"changes": {}, "deletions": {ProcessUpdates.serviceDetails: {ServiceDetails.model: modelOfThisProcess[FileObjectContent.id]}}}
        message, flag = updateProcessFunction(request, changes, currentProjectID, [processID])
        if flag is False:
            return JsonResponse({}, status=401)
        if isinstance(message, Exception):
            raise message

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},model {modelOfThisProcess[FileObjectContent.id]}," + str(datetime.now()))        
        return HttpResponse("Success", status=200)
    except (Exception) as error:
        loggerError.error(f"Error while deleting file: {str(error)}")
        return HttpResponse("Failed", status=500)
