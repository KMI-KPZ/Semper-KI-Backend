"""
Part of Semper-KI software

Silvio Weging 2023

Contains: handling of model files
"""

import logging
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from code_General.utilities import crypto
from code_General.connections.postgresql import pgProfiles
from code_General.connections import s3
from code_General.definitions import FileObjectContent
from code_General.utilities.basics import Logging, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import ProcessDescription, ProcessUpdates, DataType
from code_SemperKI.handlers.projectAndProcessManagement import updateProcessFunction #TODO

from ..definitions import ServiceDetails

logger = logging.getLogger("logToFile")

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
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
        
        model = {fileName: {}}
        model[fileName][FileObjectContent.id] = fileID
        model[fileName][FileObjectContent.title] = fileName
        model[fileName][FileObjectContent.tags] = fileTags
        model[fileName][FileObjectContent.date] = str(timezone.now())
        model[fileName][FileObjectContent.licenses] = fileLicenses
        model[fileName][FileObjectContent.certificates] = fileCertificates
        model[fileName][FileObjectContent.URI] = ""
        model[fileName][FileObjectContent.createdBy] = userName

        returnVal = s3.manageLocalS3.uploadFile(processID+"/"+fileID, request.FILES.getlist(fileName)[0])
        if returnVal is not True:
            return JsonResponse({}, status=500)
        
        # Save into files field of the process 
        # TODO!!!
        changes = {"changes": {ProcessUpdates.files: model, ProcessUpdates.serviceDetails: {ServiceDetails.model: model[fileName]}}}
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False:
            return JsonResponse({}, status=401)
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},model {fileName},"+str(datetime.now()))
        return JsonResponse(model)
    except (Exception) as error:
        logger.error(f"Error while uploading model: {str(error)}")
        return JsonResponse({}, status=500)