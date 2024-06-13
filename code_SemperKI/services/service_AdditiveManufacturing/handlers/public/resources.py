"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Calls to ontology for adding and retrieving data
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

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfRightsAreSufficient, checkIfUserIsLoggedIn, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementOrganization

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.serviceManager import serviceManager

from ...utilities import sparqlQueries
from ...service import SERVICE_NUMBER

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################

# get list of all printer/material

# get list of items for orga

# set printer/material for orga (keep in mind: one item at the time for sparql)
#######################################################
#######################################################
class SReqOrgaAddMaterial(serializers.Serializer):
    materialID = serializers.CharField(max_length=200)
    printerID = serializers.CharField(max_length=200)

#######################################################
@extend_schema(
    summary="Links an existing printer and material to an organization in the knowledge graph",
    description=" ",
    request=SReqOrgaAddMaterial,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=False)
@api_view(["POST"])
@checkVersion(0.3)
def orga_addMaterial(request:Request):
    """
    Links an existing printer and material to an organization in the knowledge graph

    :param request: POST Request
    :type request: HTTP POST
    :return: Succes or not
    :rtype: HTTP Response

    """
    try:

        serializedInput = SReqOrgaAddMaterial(request.data)
        if not serializedInput.is_valid():
            message = f"Verification failed in {orga_addMaterial.cls.__name__}"
            exception = "Verification failed"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        materialID = serializedInput.data["materialID"]
        printerID = serializedInput.data["printerID"]

        #Check that this orga provides AM as service
        if SERVICE_NUMBER not in ProfileManagementOrganization.getSupportedServices(orgaID):
            message = f"Orga does not offer service in {orga_addMaterial.cls.__name__}"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
        orgaName = ProfileManagementOrganization.getOrganizationName(orgaID)
        sparqlQueries.createEntryForContractor.sendQuery(
            {sparqlQueries.SparqlParameters.ID: orgaID, 
             sparqlQueries.SparqlParameters.name: orgaName,
             sparqlQueries.SparqlParameters.Material: materialID, 
             sparqlQueries.SparqlParameters.PrinterModel: printerID})
        
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {orga_addMaterial.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# delete printer/material for orga

