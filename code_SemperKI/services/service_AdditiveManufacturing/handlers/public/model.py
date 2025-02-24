"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Handling of model files
"""

import logging
from django.views.decorators.http import require_http_methods

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema


from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkVersion

from code_SemperKI.definitions import *
from code_SemperKI.utilities.serializer import ExceptionSerializer

from ...logics.modelLogic import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

#######################################################
class mbbDimensionsSerializer(serializers.Serializer):
    _1= serializers.FloatField()
    _2= serializers.FloatField()
    _3= serializers.FloatField()

#######################################################
class MeasurementsSerializer(serializers.Serializer):
    volume= serializers.FloatField()
    surfaceArea= serializers.FloatField()
    mbbDimensions = mbbDimensionsSerializer()
    mbbVolume= serializers.FloatField()

#######################################################
class SResCheckModel(serializers.Serializer):
    filename = serializers.CharField()
    measurements = MeasurementsSerializer()
    status_code = serializers.IntegerField()

#######################################################
@extend_schema(
    summary="Calculate model properties like boundary and volume",
    description=" ",
    tags=['FE - AM Check model'],
    request=None,
    responses={
        200: SResCheckModel,
        401: ExceptionSerializer,
        404: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def checkModel(request:Request, projectID:str, processID:str, fileID:str):
    """
    Calculate model properties like boundary and volume

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with dimensions and such
    :rtype: JSON Response

    """
    try:
        result, statusCode = logicForCheckModel(request, checkModel.cls.__name__, projectID, processID, fileID)
        if isinstance(result, Exception):
            message = f"Error in {checkModel.cls.__name__}: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        outputSerializer = SResCheckModel(data=result)
        if outputSerializer.is_valid():
            return Response(outputSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception("Validation failed " + str(outputSerializer.errors))
    except (Exception) as error:
        message = f"Error in {checkModel.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
class SReqUploadModels(serializers.Serializer):
    projectID = serializers.CharField(max_length=200, required=True)
    processID = serializers.CharField(max_length=200, required=True)
    groupID = serializers.IntegerField()
    details = serializers.CharField(default='[{"details":{"date":"2024-07-10T14:09:05.252Z","certificates":[""],"licenses":["CC BY-SA"],"tags":[""],"quantity":1,"levelOfDetail":1,"scalingFactor":100.0},"fileName":"file.stl"}]', max_length=10000)
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
            exception = f"Validation failed {serializedContent.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        info = serializedContent.data
        
        exception, value = logicForUploadModel(info, request)
        if exception is not None:
            message = str(exception)
            loggerError.error(exception)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=value)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in uploadModels: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

#######################################################
class SReqUploadWithoutFile(serializers.Serializer):
    projectID = serializers.CharField(max_length=513)
    processID = serializers.CharField(max_length=513)
    groupID = serializers.IntegerField()
    levelOfDetail = serializers.FloatField()
    width = serializers.FloatField()
    height = serializers.FloatField()
    length = serializers.FloatField()
    volume = serializers.FloatField(required=False)
    quantity = serializers.IntegerField()
    tags = serializers.ListField(child=serializers.CharField(allow_blank=True, required=False), required=False, allow_empty=True)
    origin = serializers.CharField(default="Service",max_length=200)
    name = serializers.CharField(max_length=200)
    complexity = serializers.IntegerField()
        
#######################################################
@extend_schema(
    summary="Upload a model but without the file",
    description=" ",
    tags=['FE - AM Models'],
    request=SReqUploadWithoutFile,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def uploadModelWithoutFile(request:Request):
    """
    Upload a model but without the file

    :param request: POST Request
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse

    """
    try:
        inSerializer = SReqUploadWithoutFile(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {uploadModelWithoutFile.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        retVal, value = logicForUploadModelWithoutFile(validatedInput, request)
        if retVal is not None:
            message = str(retVal)
            loggerError.error(retVal)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": retVal})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=value)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {uploadModelWithoutFile.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
class SReqUploadModelsFromRepo(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    processID = serializers.CharField(max_length=200)
    groupID = serializers.IntegerField()
    model = serializers.DictField()
    origin = serializers.CharField(default="Service",max_length=200)

#######################################################
@extend_schema(
    summary="Upload a model from the repository",
    description=" ",
    tags=['FE - AM Models'],
    request=SReqUploadModelsFromRepo,
    responses={
        200: None,
        401: ExceptionSerializer,
        404: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def uploadFromRepository(request:Request):
    """
    Upload a model from the repository

    :param request: POST Request
    :type request: HTTP POST
    :return: Successful or not
    :rtype: Response

    """
    try:
        inSerializer = SReqUploadModelsFromRepo(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {uploadFromRepository.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data

        exception, value = logicForUploadFromRepository(request, validatedInput)
        if exception is not None:
            message = str(exception)
            loggerError.error(exception)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=value)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {uploadFromRepository.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
class SReqUpdateModel(serializers.Serializer):
    projectID = serializers.CharField(max_length=513)
    processID = serializers.CharField(max_length=513)
    groupID = serializers.IntegerField()
    id = serializers.CharField(max_length=513)
    levelOfDetail = serializers.FloatField()
    quantity = serializers.IntegerField()
    isFile = serializers.BooleanField()
    tags = serializers.ListField(child=serializers.CharField(allow_blank=True, required=False), required=False, allow_empty=True)
    licenses = serializers.ListField(child=serializers.CharField(allow_blank=True, required=False), required=False, allow_empty=True)
    certificates = serializers.ListField(child=serializers.CharField(allow_blank=True, required=False), required=False, allow_empty=True)
    fileName = serializers.CharField(max_length=200, required=False)
    complexity = serializers.IntegerField(required=False)
    width = serializers.FloatField(required=False)
    height = serializers.FloatField(required=False)
    length = serializers.FloatField(required=False)
    volume = serializers.FloatField(required=False)
    scalingFactor = serializers.FloatField(required=False)
#######################################################
@extend_schema(
    summary="Update a model",
    description=" ",
    tags=['FE - AM Models'],
    request=SReqUpdateModel,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["PATCH"])
@api_view(["PATCH"])
@checkVersion(0.3)
def updateModel(request:Request):
    """
    Update a model

    :param request: PATCH Request
    :type request: HTTP PATCH
    :return: Success or not
    :rtype: Response

    """
    try:
        inSerializer = SReqUpdateModel(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {updateModel.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        validatedInput = inSerializer.data
        retVal, value = logicForUpdateModel(request, validatedInput)
        if retVal is not None:
            message = str(retVal)
            loggerError.error(retVal)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": retVal})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=value)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {updateModel.cls.__name__}: {str(error)}"
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
def deleteModel(request:Request, projectID:str, processID:str, groupID:str, fileID:str):
    """
    Delete the model and the file with it, if not done already

    :param request: DELETE Request
    :type request: HTTP DELETE
    :return: Successful or not
    :rtype: Response

    """
    try:
        result, statusCode = logicForDeleteModel(request, projectID, processID, groupID, fileID, deleteModel.cls.__name__)
        if result is not None:
            message = str(result)
            loggerError.error(result)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": result})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        outDict = logicForGetModelRepository()
        if isinstance(outDict,Exception):
            raise outDict

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