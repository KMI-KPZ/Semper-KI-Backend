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

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.definitions import *
from code_SemperKI.logics.processLogics import updateProcessFunction
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.services.service_AdditiveManufacturing.utilities import sparqlQueries
from code_SemperKI.services.service_AdditiveManufacturing.definitions import PostProcessDetails, ServiceDetails
from code_SemperKI.services.service_AdditiveManufacturing.utilities import mocks
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.serializer import ExceptionSerializer

from ...definitions import NodeTypesAM, NodePropertiesAMAdditionalRequirement

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
# Serializers
#######################################################
class SReqPostProcessingsFilter(serializers.Serializer):
    filters = serializers.ListField(child=serializers.DictField())

#######################################################
class SReqPostProcessingsContent(serializers.Serializer):
    id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)
    checked = serializers.BooleanField()
    selectedValue = serializers.CharField(allow_blank=True)
    propList = serializers.ListField()
    type = serializers.CharField(allow_blank=True)
    imgPath = serializers.CharField(max_length=200) 

#######################################################
class SResPostProcessingsWithFilters(serializers.Serializer):
    postProcessings = serializers.ListField(child=SReqPostProcessingsContent())

#######################################################
@extend_schema(
    summary="Return all postProcessings conforming to the filter",
    description=" ",
    tags=['FE - AM Additional Requirements'],
    request=SReqPostProcessingsFilter,
    responses={
        200: SResPostProcessingsWithFilters,
        400: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["POST"])
@api_view(["POST"])
@checkVersion(0.3)
def retrievePostProcessingsWithFilter(request:Request):
    """
    Return all postprocessings conforming to the filter

    :param request: POST Request
    :type request: HTTP POST
    :return: JSON with postprocessings
    :rtype: Response

    """
    try:
        inSerializer = SReqPostProcessingsFilter(data=request.data)
        if not inSerializer.is_valid():
            message = f"Verification failed in {retrievePostProcessingsWithFilter.cls.__name__}"
            exception = f"Verification failed {inSerializer.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        filters = inSerializer.data
        output = {"postProcessings": []}
        
        #filtersForSparql = []
        #for entry in filters["filters"]:
        #    filtersForSparql.append([entry["question"]["title"], entry["answer"]])
        #TODO ask via sparql with most general filter and then iteratively filter response
        """ resultsOfQueries = {"postProcessings": []}
        postProcessingsRes = cmem.getAllMaterials.sendQuery()
        for elem in postProcessingsRes:
            title = elem["Material"]["value"]
            resultsOfQueries["postProcessings"].append({"id": crypto.generateMD5(title), "title": title, "propList": [], "imgPath": mocks.testpicture})
        output.update(resultsOfQueries["postProcessings"]) """
        
        # TODO calculate price

        postProcessings = pgKnowledgeGraph.Basics.getNodesByType(NodeTypesAM.additionalRequirement)
        filteredOutput = [entry for entry in postProcessings if entry[pgKnowledgeGraph.NodeDescription.createdBy] == pgKnowledgeGraph.defaultOwner] # and entry[pgKnowledgeGraph.NodeDescription.active] == True] # use only entries from system

        for entry in filteredOutput:
            imgPath = entry[pgKnowledgeGraph.NodeDescription.properties][NodePropertiesAMAdditionalRequirement.imgPath] if NodePropertiesAMAdditionalRequirement.imgPath in entry[pgKnowledgeGraph.NodeDescription.properties] else mocks.testPicture
            output["postProcessings"].append({"id": entry[pgKnowledgeGraph.NodeDescription.nodeID], "title": entry[pgKnowledgeGraph.NodeDescription.nodeName], "checked": False, "selectedValue": "", "type": "text", "propList": entry[pgKnowledgeGraph.NodeDescription.properties], "imgPath": imgPath})
            # TODO use translation here for nodeName
        # mockup here:
        #mock = copy.deepcopy(mocks.postProcessingMock)
        #output.update(mock)
        
        outSerializer = SResPostProcessingsWithFilters(data=output)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in {retrievePostProcessingsWithFilter.cls.__name__}: {str(error)}"
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
class SReqSetPostProcessings(serializers.Serializer):
    projectID = serializers.CharField(max_length=200)
    processID = serializers.CharField(max_length=200)
    postProcessings = serializers.ListField(child=SReqPostProcessingsContent())
    groupID = serializers.IntegerField()
    
#######################################################
@extend_schema(
    summary="User selected a postprocessing",
    description=" ",
    tags=['FE - AM Additional Requirements'],
    request=SReqSetPostProcessings,
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
def setPostProcessingSelection(request:Request):
    """
    User selected a postprocessing

    :param request: PATCH Request
    :type request: HTTP PATCH
    :return: Success or Exception
    :rtype: HTTP Response

    """
    try:
        serializedContent = SReqSetPostProcessings(data=request.data)
        if not serializedContent.is_valid():
            message = "Validation failed in setPostProcessingSelection"
            exception = f"Validation failed {serializedContent.errors}"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        info = serializedContent.data
        projectID = info[ProjectDescription.projectID]
        processID = info[ProcessDescription.processID]
        postProcessings = info["postProcessings"]
        groupID = info["groupID"]

        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface()
        if interface == None:
            return (Exception(f"Rights not sufficient in {setPostProcessingSelection.cls.__name__}"), 401)

        postProcessingToBeSaved = {} 
        for postProcessing in postProcessings:
            postProcessingToBeSaved[postProcessing[PostProcessDetails.id]] = postProcessing

        existingGroups = interface.getProcessObj(projectID, processID).serviceDetails[ServiceDetails.groups]
        updateArray = [{} for i in range(len(existingGroups))]
        updateArray[groupID] = {ServiceDetails.postProcessings: postProcessingToBeSaved}
        changes = {"changes": {ProcessUpdates.serviceDetails: {ServiceDetails.groups: updateArray}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            message = f"Rights not sufficient for {setPostProcessingSelection.cls.__name__}"
            exception = "Unauthorized"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},set,{Logging.Object.OBJECT},postProcessing,"+str(datetime.now()))
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {setPostProcessingSelection.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

#######################################################
@extend_schema(
    summary="Remove a prior selected postProcessing from selection",
    description=" ",
    tags=['FE - AM Additional Requirements'],
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
def deletePostProcessingFromSelection(request:Request,projectID:str,processID:str,groupID:int,postProcessingID:str):
    """
    Remove a prior selected postProcessing from selection

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param projectID: Project ID
    :type projectID: str
    :param processID: Process ID
    :type processID: str
    :param postProcessingID: ID of the selected postProcessing
    :type postProcessingID: str
    :param groupID: Index of the group
    :type groupID: str
    :return: Success or Exception
    :rtype: HTTP Response

    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface()
        if interface == None:
            return (Exception(f"Rights not sufficient in {deletePostProcessingFromSelection.cls.__name__}"), 401)
        
        existingGroups = interface.getProcessObj(projectID, processID).serviceDetails[ServiceDetails.groups]
        updateArray = [{} for i in range(len(existingGroups))]
        updateArray[groupID] = {ServiceDetails.postProcessings: {postProcessingID: ""}}
        changes = {"deletions": {ProcessUpdates.serviceDetails: {ServiceDetails.groups: updateArray}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            message = f"Rights not sufficient for {deletePostProcessingFromSelection.cls.__name__}"
            exception = "Unauthorized"
            loggerError.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},deleted,{Logging.Object.OBJECT},postProcessing,"+str(datetime.now()))
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {deletePostProcessingFromSelection.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)