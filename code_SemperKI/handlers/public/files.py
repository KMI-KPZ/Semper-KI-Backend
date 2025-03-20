"""
Part of Semper-KI software

Silvio Weging 2023

Contains: File upload handling
"""

import logging
import os
from logging import getLogger

from rest_framework import status, serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from Generic_Backend.code_General.utilities.basics import checkVersion, checkIfUserIsLoggedIn, checkIfRightsAreSufficient
from Generic_Backend.code_General.utilities.files import createFileResponse
from Generic_Backend.code_General.definitions import FileObjectContent

from code_SemperKI.utilities.serializer import ExceptionSerializer
from ...utilities.basics import checkIfUserMaySeeProcess
from ...logics.filesLogics import *

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
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        info = inSerializer.data
        result, statusCode = logicForUploadFiles(request, info, uploadFiles.cls.__name__)
        if result is not None:
            message = f"Error while uploading files: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        fileMetaData, flag = getFilesInfoFromProcess(request.session, projectID, processID, fileID)
        if flag is False:
            return fileMetaData

        encryptionAdapter, flag = getFileReadableStream(request.session, projectID, processID, fileID)
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
    },
    parameters=[OpenApiParameter(
        name='fileIDs',
        type={'type': 'array', 'minItems': 1, 'items': {'type': 'string'}},
        location=OpenApiParameter.QUERY,
        required=True,
        style='form',
        explode=False,
    )],
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
        fileResponse = logicForDownloadAsZip(request, projectID, processID, downloadFilesAsZip.cls.__name__)
        #if isinstance(fileResponse, FileResponse):
            #fileResponse["Content-Disposition"] = f'attachment; filename="{processID}.zip"'.format(f"{processID}.zip")
        return fileResponse

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
        return logicForDownloadProcessHistory(request, processID, downloadProcessHistory.__name__)
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
        result, statusCode = logicForDeleteFile(request, projectID, processID, fileID, deleteFile.__name__)
        if isinstance(result, Exception):
            message = f"Error while deleting files: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
