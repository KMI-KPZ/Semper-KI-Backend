"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Handling of model files
"""

import json, logging, copy
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from django.core.handlers.asgi import ASGIRequest

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import *
from code_SemperKI.handlers.files import deleteFile
from code_SemperKI.handlers.public.process import updateProcessFunction
from code_SemperKI.services.service_AdditiveManufacturing.definitions import ServiceDetails
from code_SemperKI.utilities.basics import *
from code_SemperKI.connections.content.manageContent import ManageContent
from MSQ.tasks.tasks import callfTetWild
from MSQ.handlers.interface import returnFileFromfTetWild

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

#######################################################
class SReqUploadModels(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    processID = serializers.CharField(max_length=200)
    details = serializers.CharField(max_length=10000)
    # multipart/form-data


#######################################################
@extend_schema(
    summary="File upload for multiple files",
    description=" ",
    request={
        "multipart/form-data": SReqUploadModels
    },	
    #request=SReqUploadModels,
    responses={
        200: None,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["POST"])
@api_view(["POST"])
def uploadModels(request:Request):
    """
    File upload for multiple files.
    TODO: Verify files, python-magic could help, or https://github.com/mbourqui/django-constrainedfilefield as well as https://stackoverflow.com/questions/20272579/django-validate-file-type-of-uploaded-file

    :param request: POST Request
    :type request: HTTP POST
    :return: Response with information about the file
    :rtype: Response

    """
    try:
        serializedContent = SReqUploadModels(data=request.data)
        if not serializedContent.is_valid():
            message = "Validation failed"
            exception = "Validation failed"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        info = serializedContent.data
        projectID = info[ProjectDescription.projectID]
        processID = info[ProcessDescription.processID]

        content = ManageContent(request.session)
        interface = content.getCorrectInterface(updateProcessFunction.__name__) # if that fails, no files were uploaded and nothing happened
        if interface == None:
            message = "Rights not sufficient in uploadModel"
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
        
        detailsOfAllFiles = json.loads(info["details"])
        models = {}
        for key in request.data:
            if key != ProjectDescription.projectID and key != ProcessDescription.processID and key != "details":
                models[key] = request.data[key]
        modelsToBeSaved = {}
        for fileName in models:
            model = models[fileName]
            details = {}
            for detail in detailsOfAllFiles: # details are not in the same order as the models
                if detail["fileName"] == fileName:
                    details = detail["details"]
                    break
            fileID = crypto.generateURLFriendlyRandomString()
            filePath = processID+"/"+fileID
            userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
            modelsToBeSaved[fileID] = {}
            modelsToBeSaved[fileID][FileObjectContent.id] = fileID
            modelsToBeSaved[fileID][FileObjectContent.fileName] = fileName
            modelsToBeSaved[fileID][FileObjectContent.tags] = details["tags"]
            modelsToBeSaved[fileID][FileObjectContent.date] = str(timezone.now())
            modelsToBeSaved[fileID][FileObjectContent.licenses] = details["licenses"]
            modelsToBeSaved[fileID][FileObjectContent.certificates] = details["certificates"]
            modelsToBeSaved[fileID][FileObjectContent.URI] = ""
            modelsToBeSaved[fileID][FileObjectContent.createdBy] = userName
            modelsToBeSaved[fileID][FileObjectContent.path] = filePath

            if remote:
                modelsToBeSaved[fileID][FileObjectContent.remote] = True
                returnVal = s3.manageRemoteS3.uploadFile(filePath, model)
                if returnVal is not True:
                    raise Exception(f"File {fileName} could not be saved to remote storage")
            else:
                modelsToBeSaved[fileID][FileObjectContent.remote] = False
                returnVal = s3.manageLocalS3.uploadFile(filePath, model)
                if returnVal is not True:
                    raise Exception(f"File {fileName} could not be saved to local storage")
                
        changes = {"changes": {ProcessUpdates.files: modelsToBeSaved, ProcessUpdates.serviceDetails: {ServiceDetails.models: modelsToBeSaved}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            message = "Rights not sufficient for uploadModel"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},models,"+str(datetime.now()))
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in uploadModel: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        
    
#######################################################
@extend_schema(
    summary="Delete the model and the file with it, if not done already",
    description=" ",
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        404: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["DELETE"])
@api_view(["DELETE"])
def deleteModel(request:Request, projectID:str, processID:str, fileID:str):
    """
    Delete the model and the file with it, if not done already

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: Successful or not
    :rtype: Response

    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(updateProcessFunction.__name__)
        if interface == None:
            message = "Rights not sufficient in deleteModel"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        currentProcess = interface.getProcessObj(projectID, processID)
        modelsOfThisProcess = currentProcess.serviceDetails[ServiceDetails.models]
        if fileID not in modelsOfThisProcess or fileID not in currentProcess.files:
            message = "Model not found in deleteModel"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        deleteFile(request, projectID, processID, fileID)
        
        changes = {"changes": {}, "deletions": {ProcessUpdates.serviceDetails: {ServiceDetails.models: {fileID}}}}
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False:
            message = "Rights not sufficient in deleteModel"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if isinstance(message, Exception):
            raise message

        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},model {fileID}," + str(datetime.now()))        
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in deleteModel: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################
@extend_schema(
    summary="Converts an uploaded stl file to a file with tetrahedral mesh",
    description=" ",
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        404: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["GET"])
@api_view(["GET"])
def remeshSTLToTetraheadras(request:Request, projectID:str, processID:str, fileID:str):
    """
    Converts an uploaded stl file to a file with tetrahedral mesh

    :param request: GET Request
    :type request: HTTP GET
    :return: Indirectly a file (via Celery)
    :rtype: (File)Response

    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(updateProcessFunction.__name__)
        if interface == None:
            message = "Rights not sufficient in deleteModel"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        currentProcess = interface.getProcessObj(projectID, processID)
        modelsOfThisProcess = currentProcess.serviceDetails[ServiceDetails.models]
        if fileID not in modelsOfThisProcess or fileID not in currentProcess.files:
            message = "Model not found in deleteModel"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        modelsOfThisProcess[fileID][FileObjectContent.path]
        filePath, _ = callfTetWild(modelsOfThisProcess[fileID][FileObjectContent.path])
        if filePath == "":
            raise Exception("Calculation failed!")
        return returnFileFromfTetWild(filePath)
        #return Response("Success")
    except (Exception) as error:
        message = f"Error in remeshSTLToTetraheadras: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)