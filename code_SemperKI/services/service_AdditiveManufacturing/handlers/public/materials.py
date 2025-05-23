"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Handlers for AM Materials
"""

import json, logging, copy, numpy
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient
from Generic_Backend.code_General.connections.redis import RedisConnection

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.definitions import *
from code_SemperKI.logics.processLogics import updateProcessFunction
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.services.service_AdditiveManufacturing.utilities import sparqlQueries
from code_SemperKI.services.service_AdditiveManufacturing.definitions import MaterialDetails, ServiceDetails
from code_SemperKI.services.service_AdditiveManufacturing.utilities import mocks
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.serializer import ExceptionSerializer

from ...definitions import NodeTypesAM, NodePropertiesAMMaterial
from ...logics.materialsLogic import logicForSetMaterial, logicForRetrieveMaterialWithFilter

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
# Serializer
#######################################################
class SReqMaterialsFilter(serializers.Serializer):
    filters = serializers.ListField(child=serializers.DictField())

#######################################################
class SReqMaterialContent(serializers.Serializer):
    id = serializers.CharField(max_length=200)
    title = serializers.CharField(max_length=200)
    propList = serializers.ListField()
    imgPath = serializers.CharField(max_length=200)
    medianPrice = serializers.FloatField(required=False)
    colors = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)

#######################################################
class SResMaterialsWithFilters(serializers.Serializer):
    materials = serializers.ListField(child=SReqMaterialContent())

#######################################################
@extend_schema(
    summary="Return all materials conforming to the filter",
    description=" ",
    tags=['FE - AM Materials'],
    request=SReqMaterialsFilter,
    responses={
        200: SResMaterialsWithFilters,
        400: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def retrieveMaterialsWithFilter(request:Request):
    """
    Return all materials conforming to the filter

    :param request: POST Request
    :type request: HTTP POST
    :return: JSON with materials
    :rtype: Response

    """
    try:
        inSerializer = SReqMaterialsFilter(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {retrieveMaterialsWithFilter.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        filters = inSerializer.data
        # get language settings from session
        locale = pgProfiles.ProfileManagementBase.getUserLocale(request.session)
        result, statusCode = logicForRetrieveMaterialWithFilter(filters, locale)
        if isinstance(result, Exception):
            message = f"Error in retrieveMaterialsWithFilter: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        outSerializer = SResMaterialsWithFilters(data=result)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in retrieveMaterialsWithFilter: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################
# Serializer

#######################################################
class SReqSetMaterial(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    processID = serializers.CharField(max_length=200)
    groupID = serializers.IntegerField()
    material = SReqMaterialContent()
    color = serializers.DictField(required=False, allow_empty=True)
    
#######################################################
@extend_schema(
    summary="User selected a material",
    description=" ",
    tags=['FE - AM Materials'],
    request=SReqSetMaterial,
    responses={
        200: None,
        400: ExceptionSerializer,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["PATCH"])
@api_view(["PATCH"])
@checkVersion(0.3)
def setMaterialSelection(request:Request):
    """
    User selected a material

    :param request: PATCH Request
    :type request: HTTP PATCH
    :return: Success or Exception
    :rtype: HTTP Response

    """
    try:
        serializedContent = SReqSetMaterial(data=request.data)
        if not serializedContent.is_valid():
            message = "Validation failed in setMaterialSelection"
            exception = f"Validation failed {serializedContent.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        info = serializedContent.data
        
        result, statusCode = logicForSetMaterial(request, info, setMaterialSelection.cls.__name__)
        if isinstance(result, Exception):
            message = f"Error in addMaterialToSelection: {str(result)}"
            exception = str(result)
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=statusCode)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in addMaterialToSelection: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

#######################################################
@extend_schema(
    summary="Remove a prior selected material from selection",
    description=" ",
    tags=['FE - AM Materials'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["DELETE"])
@api_view(["DELETE"])
@checkVersion(0.3)
def deleteMaterialFromSelection(request:Request,projectID:str,processID:str,groupID:int):
    """
    Remove a prior selected material from selection

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param projectID: Project ID
    :type projectID: str
    :param processID: Process ID
    :type processID: str
    :param groupID: Index of the group
    :type groupID: int
    :return: Success or Exception
    :rtype: HTTP Response

    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface()
        if interface == None:
            message = "Rights not sufficient for deleteMaterialFromSelection"
            exception = "Unauthorized"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get the process
        process = interface.getProcessObj(projectID, processID)
        if isinstance(process, Exception):
            message = "Process not found in deleteMaterialFromSelection"
            exception = "Not found"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        changesArray = [{} for i in range(len(process.serviceDetails[ServiceDetails.groups]))]
        changesArray[groupID] = {ServiceDetails.material: {}}
        changes = {"deletions": {ProcessUpdates.serviceDetails: {ServiceDetails.groups: changesArray}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            message = "Rights not sufficient for deleteMaterialFromSelection"
            exception = "Unauthorized"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},deleted,{Logging.Object.OBJECT},material,"+str(datetime.now()))
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in deleteMaterialFromSelection: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)