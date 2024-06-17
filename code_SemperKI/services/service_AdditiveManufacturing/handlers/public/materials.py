"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Handlers for AM Materials
"""

import json, logging, copy
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

from code_SemperKI.definitions import *
from code_SemperKI.handlers.projectAndProcessManagement import updateProcessFunction
from code_SemperKI.services.service_AdditiveManufacturing.utilities import sparqlQueries
from code_SemperKI.services.service_AdditiveManufacturing.definitions import MaterialDetails, ServiceDetails
from code_SemperKI.services.service_AdditiveManufacturing.utilities import mocks
from code_SemperKI.utilities.basics import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
# Serializer
#######################################################
class SReqMaterialsFilter(serializers.Serializer):
    filters = serializers.ListField(child=serializers.DictField())

#######################################################
class SReqMaterialContent(serializers.Serializer):
    id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)
    propList = serializers.ListField()
    imgPath = serializers.CharField(max_length=200) 

#######################################################
class SResMaterialsWithFilters(serializers.Serializer):
    materials = serializers.ListField(child=SReqMaterialContent())

#######################################################
@extend_schema(
    summary="Return all materials conforming to the filter",
    description=" ",
    request=SReqMaterialsFilter,
    responses={
        200: SResMaterialsWithFilters,
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
            exception = "Verification failed"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        filters = inSerializer.data
        output = {"materials": []}
        
        #filtersForSparql = []
        #for entry in filters["filters"]:
        #    filtersForSparql.append([entry["question"]["title"], entry["answer"]])
        #TODO ask via sparql with most general filter and then iteratively filter response
        resultsOfQueries = {"materials": []}
        materialsRes = sparqlQueries.getAllMaterials.sendQuery()
        for elem in materialsRes:
            title = elem["Material"]["value"]
            resultsOfQueries["materials"].append({"id": crypto.generateMD5(title), "title": title, "propList": [], "imgPath": mocks.testpicture.mockPicturePath})

        
        # mockup here:
        mock = copy.deepcopy(mocks.materialMock)
        mock["materials"].extend(resultsOfQueries["materials"])
        output.update(mock)

        outSerializer = SResMaterialsWithFilters(data=output)
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
    material = SReqMaterialContent()
    
#######################################################
@extend_schema(
    summary="User selected a material",
    description=" ",
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
        material = info["material"]

        materialToBeSaved = {material[MaterialDetails.id]: material}

        changes = {"changes": {ProcessUpdates.serviceDetails: {ServiceDetails.materials: materialToBeSaved}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            message = "Rights not sufficient for setMaterialSelection"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},added,{Logging.Object.OBJECT},material,"+str(datetime.now()))
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
def deleteMaterialFromSelection(request:Request,projectID:str,processID:str,materialID:str):
    """
    Remove a prior selected material from selection

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param projectID: Project ID
    :type projectID: str
    :param processID: Process ID
    :type processID: str
    :param materialID: ID of the selected material
    :type materialID: str
    :return: Success or Exception
    :rtype: HTTP Response

    """
    try:
        changes = {"deletions": {ProcessUpdates.serviceDetails: {ServiceDetails.materials: {materialID: ""}}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            message = "Rights not sufficient for deleteMaterialFromSelection"
            exception = "Unauthorized"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},added,{Logging.Object.OBJECT},material,"+str(datetime.now()))
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