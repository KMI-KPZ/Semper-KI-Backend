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
#######################################################
class SResMaterialList(serializers.Serializer):
    materials = serializers.ListField() #TODO specify
#######################################################
@extend_schema(
    summary="Gathers all available materials from the KG",
    description=" ",
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
@checkVersion(0.3)
def onto_getMaterials(request:Request):
    """
    Gathers all available materials from the KG

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with Materials available
    :rtype: JSON Response

    """
    try:
        resultsOfQueries = {"materials": []}
        materialsRes = sparqlQueries.getAllMaterials.sendQuery()
        for elem in materialsRes:
            title = elem["Material"]["value"]
            resultsOfQueries["materials"].append({"title": title, "URI": elem["Material"]["value"]})
        
        outSerializer = SResMaterialList(data=resultsOfQueries)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)

    except (Exception) as error:
        message = f"Error in {onto_getMaterials.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
class SResPrinters(serializers.Serializer):
    printers = serializers.ListField() # TODO specify

#######################################################
@extend_schema(
    summary="Gathers all available 3D printers from KG",
    description=" ",
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
@checkVersion(0.3)
def onto_getPrinters(request:Request):
    """
    Gathers all available 3D printers from KG

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with list of printers
    :rtype: JSON Response

    """
    try:
        resultsOfQueries = {"printers": []}
        printersRes = sparqlQueries.getAllPrinters.sendQuery()
        for elem in printersRes:
            title = elem["3DPrinter_name"]["value"]
            resultsOfQueries["printers"].append({"title": title, "URI": elem["3DPrinter_name"]["value"]})
        
        outSerializer = SResPrinters(data=resultsOfQueries)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
            
    except (Exception) as error:
        message = f"Error in {onto_getPrinters.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# get list of items for orga
#######################################################
class SResOrgaResources(serializers.Serializer):
    pass # TODO

#######################################################
@extend_schema(
    summary="Retrieve all KG information about connected resources for an organization",
    description=" ",
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
@checkVersion(0.3)
def orga_getResources(request:Request):
    """
    Retrieve all KG information about connected resources for an organization

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON with list of resources
    :rtype: JSON Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)

        #Check that this orga provides AM as service
        if SERVICE_NUMBER not in ProfileManagementOrganization.getSupportedServices(orgaID):
            message = f"Orga does not offer service in {orga_addMaterialToPrinter.cls.__name__}"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        result = sparqlQueries.getServiceProviders.sendQuery({sparqlQueries.SparqlParameters.ID: orgaID})
        # TODO: Parse and serialize output
        
        return Response(result, status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {orga_getResources.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# set printer/material for orga (keep in mind: one item at the time for sparql)
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
def orga_addMaterialToPrinter(request:Request):
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
            message = f"Verification failed in {orga_addMaterialToPrinter.cls.__name__}"
            exception = "Verification failed"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        materialID = serializedInput.data["materialID"] #TODO how must this be coded?
        printerID = serializedInput.data["printerID"]

        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
        orgaName = ProfileManagementOrganization.getOrganizationName(orgaID)

        #Check that this orga provides AM as service
        if SERVICE_NUMBER not in ProfileManagementOrganization.getSupportedServices(orgaID):
            message = f"Orga does not offer service in {orga_addMaterialToPrinter.cls.__name__}"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        sparqlQueries.createEntryForContractor.sendQuery(
            {sparqlQueries.SparqlParameters.ID: orgaID, 
             sparqlQueries.SparqlParameters.name: orgaName,
             sparqlQueries.SparqlParameters.Material: materialID, 
             sparqlQueries.SparqlParameters.PrinterModel: printerID})
        
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {orga_addMaterialToPrinter.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Update information
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
@require_http_methods(["PATCH"])
@checkIfRightsAreSufficient(json=False)
@api_view(["PATCH"])
@checkVersion(0.3)
def orga_updateMaterialAndPrinter(request:Request):
    """
    Update a Link to an existing printer and material for an organization in the knowledge graph
    Can also be used to delete the connection of a printer to a material by setting it to "None"?

    :param request: PATCH Request
    :type request: HTTP PATCH
    :return: Succes or not
    :rtype: HTTP Response

    """
    try:

        serializedInput = SReqOrgaAddMaterial(request.data)
        if not serializedInput.is_valid():
            message = f"Verification failed in {orga_updateMaterialAndPrinter.cls.__name__}"
            exception = "Verification failed"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        materialID = serializedInput.data["materialID"] #TODO how must this be coded?
        printerID = serializedInput.data["printerID"]

        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
        orgaName = ProfileManagementOrganization.getOrganizationName(orgaID)

        #Check that this orga provides AM as service
        if SERVICE_NUMBER not in ProfileManagementOrganization.getSupportedServices(orgaID):
            message = f"Orga does not offer service in {orga_updateMaterialAndPrinter.cls.__name__}"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        sparqlQueries.updateEntryForContractor.sendQuery(
            {sparqlQueries.SparqlParameters.ID: orgaID, 
             sparqlQueries.SparqlParameters.name: orgaName,
             sparqlQueries.SparqlParameters.Material: materialID, 
             sparqlQueries.SparqlParameters.PrinterModel: printerID})
        
        return Response("Success", status=status.HTTP_200_OK)

    except (Exception) as error:
        message = f"Error in {orga_updateMaterialAndPrinter.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# delete printer for orga
#######################################################
@extend_schema(
    summary="Remove the connection of an organization to a printer and/or material",
    description=" ",
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@checkIfUserIsLoggedIn()
@require_http_methods(["DELETE"])
@checkIfRightsAreSufficient(json=False)
@api_view(["DELETE"])
@checkVersion(0.3)
def orga_removeLinkToPrinter(request:Request, printerID:str):
    """
    Remove the connection of an organization to a printer

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param printerID: The ID of the printer of that orga
    :type printerID: str
    :param materialID: The ID of the material from that orga that should now belong to that printer
    :type materialID: str
    :return: Success or not
    :rtype: HTTP Response

    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)

        #Check that this orga provides AM as service
        if SERVICE_NUMBER not in ProfileManagementOrganization.getSupportedServices(orgaID):
            message = f"Orga does not offer service in {orga_updateMaterialAndPrinter.cls.__name__}"
            exception = "Not found"
            logger.error(message)
            exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
            if exceptionSerializer.is_valid():
                return Response(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        sparqlQueries.deleteEntryForContractor.sendQuery(
            {sparqlQueries.SparqlParameters.ID: orgaID, 
             sparqlQueries.SparqlParameters.PrinterModel: printerID})
        
        return Response("Success", status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {orga_removeLinkToPrinter.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)