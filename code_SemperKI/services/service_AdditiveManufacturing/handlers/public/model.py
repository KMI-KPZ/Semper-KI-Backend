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
from Generic_Backend.code_General.utilities.basics import checkVersion, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import *
from code_SemperKI.handlers.public.files import deleteFile
from code_SemperKI.handlers.public.process import updateProcessFunction
from code_SemperKI.services.service_AdditiveManufacturing.definitions import ServiceDetails
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.utilities.basics import testPicture
from code_SemperKI.connections.content.manageContent import ManageContent
from MSQ.tasks.tasks import callfTetWild
from MSQ.handlers.interface import returnFileFromfTetWild

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

#######################################################
class SReqUploadModels(serializers.Serializer):
    projectID = serializers.CharField(max_length=200, required=True)
    processID = serializers.CharField(max_length=200, required=True)
    details = serializers.CharField(default='[{"details":{"date":"2024-07-10T14:09:05.252Z","certificates":[""],"licenses":["CC BY-SA"],"tags":[""]},"fileName":"file.stl"}]', max_length=10000)
    origin = serializers.CharField(default="Service",max_length=200)
    file = serializers.FileField(required=False)
    # multipart/form-data


#######################################################
@extend_schema(
    summary="File upload for multiple files",
    description=" ",
    tags=['FE - AM Models'],
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
@checkVersion(0.3)
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
        origin = info["origin"]

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
        modelNames = list(request.FILES.keys())
        modelsToBeSaved = {}
        for fileName in modelNames:
            for model in request.FILES.getlist(fileName):
                details = {}
                for detail in detailsOfAllFiles: # details are not in the same order as the models
                    if detail["fileName"] == fileName or fileName == "file":
                        details = detail["details"]
                        break
                fileID = crypto.generateURLFriendlyRandomString()
                filePath = projectID+"/"+processID+"/"+fileID
                userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
                modelsToBeSaved[fileID] = {}
                modelsToBeSaved[fileID][FileObjectContent.id] = fileID
                modelsToBeSaved[fileID][FileObjectContent.path] = filePath
                modelsToBeSaved[fileID][FileObjectContent.fileName] = fileName
                modelsToBeSaved[fileID][FileObjectContent.imgPath] = testPicture
                modelsToBeSaved[fileID][FileObjectContent.tags] = details["tags"]
                modelsToBeSaved[fileID][FileObjectContent.licenses] = details["licenses"]
                modelsToBeSaved[fileID][FileObjectContent.certificates] = details["certificates"]
                modelsToBeSaved[fileID][FileObjectContent.date] = str(timezone.now())
                modelsToBeSaved[fileID][FileObjectContent.createdBy] = userName
                modelsToBeSaved[fileID][FileObjectContent.size] = model.size
                modelsToBeSaved[fileID][FileObjectContent.type] = FileTypes.Model
                modelsToBeSaved[fileID][FileObjectContent.origin] = origin

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
    tags=['FE - AM Models'],
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
@checkVersion(0.3)
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

        deleteFile(request._request, projectID, processID, fileID)
        
        changes = {"changes": {}, "deletions": {ProcessUpdates.serviceDetails: {ServiceDetails.models: {fileID}}}}
        message, flag = updateProcessFunction(request._request, changes, projectID, [processID])
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
    tags=['BE - AM Models'],
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
@checkVersion(0.3)
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
        
#######################################################
class SResRepoContent(serializers.Serializer):
    name = serializers.CharField()
    license= serializers.CharField()
    preview=serializers.CharField()
    file=serializers.CharField()

#######################################################
class SResModelRepository(serializers.Serializer):
    repository = serializers.DictField(
        child=SResRepoContent()               
    )

#######################################################
@extend_schema(
    summary="Get previews and file names of 3D models from our curated repository",
    description=" ",
    tags=['FE - AM Models'],
    request=None,
    responses={
        200: SResModelRepository,
        500: ExceptionSerializer
    }
)
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getModelRepository(request:Request):
    """
    Get previews and file names of 3D models from our curated repository

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with names of files, link to preview files and link to files themselves
    :rtype: JSON Response

    """
    try:
        content = s3.manageRemoteS3Buckets.getContentOfBucket("ModelRepository")
        outDict = {"repository": {}}
        for elem in content:
            path = elem["Key"]
            splitPath = path.split("/")[1:]
            if len(splitPath) > 1:
                if "license" in elem["Metadata"]:
                    license = elem["Metadata"]["license"]
                else:
                    license = ""
                if splitPath[0] in outDict["repository"]:
                    if "Preview" in splitPath[1]:
                        outDict["repository"][splitPath[0]]["preview"] = s3.manageRemoteS3Buckets.getDownloadLinkPrefix()+elem["Key"].replace(" ", "%20")
                    else:
                        outDict["repository"][splitPath[0]]["file"] = s3.manageRemoteS3Buckets.getDownloadLinkPrefix()+elem["Key"].replace(" ", "%20")
                    if license != "" and outDict["repository"][splitPath[0]]["license"] == "":
                        outDict["repository"][splitPath[0]]["license"] = license
                else:
                    outDict["repository"][splitPath[0]] = {"name": splitPath[0], "license": "", "preview": "", "file": ""}
                    if "Preview" in splitPath[1]:
                        outDict["repository"][splitPath[0]]["preview"] = s3.manageRemoteS3Buckets.getDownloadLinkPrefix()+elem["Key"].replace(" ", "%20")
                    else:
                        outDict["repository"][splitPath[0]]["file"] = s3.manageRemoteS3Buckets.getDownloadLinkPrefix()+elem["Key"].replace(" ", "%20")
                    if license != "" and outDict["repository"][splitPath[0]]["license"] == "":
                        outDict["repository"][splitPath[0]]["license"] = license

        outSerializer = SResModelRepository(data=outDict)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {getModelRepository.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)