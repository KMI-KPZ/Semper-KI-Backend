"""
Part of Semper-KI software

Akshay NS 2024

Contains: Handlers for miscellaneous [services, statusbuttons]
"""

from django.conf import settings
import logging, platform, subprocess, json, requests
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods

from rest_framework import status, serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, checkVersion
from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase

from code_SemperKI.definitions import *
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.utilities.basics import checkIfUserMaySeeProcess, testPicture
from code_SemperKI.serviceManager import serviceManager, ServicesStructure



logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
loggerDebug = logging.getLogger("django_debug")
##################################################

#########################################################################
# getServices
#"getServices": ("public/getServices/", miscellaneous.getServices)
#########################################################################
# Serializer for getServices
#######################################################
class SResServices(serializers.Serializer):
    type = serializers.CharField(max_length=200)
    imgPath = serializers.URLField()
#########################################################################
# Handler    
@extend_schema(
    summary="Return the offered services",
    description=" ",
    request=None,
    tags = ['FE - Miscellaneous'],
    responses={
        200: serializers.ListSerializer(child=SResServices()),
        500: ExceptionSerializer
    }
)
@api_view(["GET"])
@checkVersion(0.3)
def getServices(request:Request):
    """
    Return the offered services

    :param request: The request object
    :type request: Dict
    :return: The Services as dictionary with string and integer coding
    :rtype: JSONResponse
    
    """
    try:
        
        services = serviceManager.getAllServices()
        services.sort(key=lambda x: x[ServicesStructure.identifier])
        outList = []
        for entry in services:
            if entry[ServicesStructure.name] == "None":
                continue
            outList.append({"type": entry[ServicesStructure.name], "imgPath": entry[ServicesStructure.imgPath]})
        outSerializer = SResServices(data=outList, many=True)
        if outSerializer.is_valid():
            return Response(outSerializer.data, status=status.HTTP_200_OK)
        else:
            raise Exception(outSerializer.errors)
    except (Exception) as error:
        message = f"Error in getServices: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

##################################################
# @extend_schema(
#     summary="Return the offered services",
#     description=" ",
#     request=None,
#     tags = ['miscellaneous'],
#     responses={
#         200: None,
#         500: ExceptionSerializer
#     }
# )
# @api_view(["POST", "GET"])
# def isMagazineUp(request:Request):
#     """
#     Pings the magazine website and check if that works or not

#     :param request: GET/POST request
#     :type request: HTTP GET/POST
#     :return: Response with True or False 
#     :rtype: JSON Response

#     """
#     if request.method == "POST":
#         try:
#             content = request.data
#             response = {"up": True}
#             for entry in content["urls"]:
#                 resp = requests.get(entry)
#                 if resp.status_code != 200:
#                     response["up"] = False
                
#             return JsonResponse(response)
#         except Exception as e:
#             return HttpResponse(e, status=500)
#     elif request.method == "GET":
#         param = '-n' if platform.system().lower()=='windows' else '-c'

#         # Building the command. Ex: "ping -c 1 google.com"
#         command = ['ping', param, '2', 'magazin.semper-ki.org', '-4']

#         response = {"up": True}
#         pRet = subprocess.run(command)
#         if pRet.returncode != 0:
#             response["up"] = False
#         return JsonResponse(response)
        
##############################################
        


#######################################################
@extend_schema(
    summary="Retrieve the results from the questionnaire made by KMI",
    description=" ",
    tags=['BE - Questionnaire'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["POST"])
@api_view(["POST"])
def retrieveResultsFromQuestionnaire(request:Request):
    """
    Retrieve the results from the questionnaire made by KMI

    :param request: POST Request
    :type request: HTTP POST
    :return: Nothing
    :rtype: ResponseRedirect

    """
    try:
        orgID = request.data["orgID"] if "orgID" in request.data else ""
        assessmentType = request.data["assessmentType"] if "assessmentType" in request.data else ""
        data = request.data["data"] if "data" in request.data else []

        if orgID != "":
            orgaObj = ProfileManagementBase.getOrganizationObject(hashID=orgID)
            if isinstance(orgaObj, Exception):
                raise ValidationError("No organization found")
            if "maturity" in assessmentType.lower():
                orgaObj.details[OrganizationDetailsSKI.maturityLevel] = [data]
            elif "resilience" in assessmentType.lower():
                orgaObj.details[OrganizationDetailsSKI.resilienceScore] = data
            else:
                raise Exception("Unknown assessment type")
            orgaObj.save()
        
        return Response()
    except (Exception) as error:
        message = f"Error in {retrieveResultsFromQuestionnaire.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#######################################################
@extend_schema(
    summary="Return the maturity level of the project",
    description=" ",
    tags=['FE - Questionnaire'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["GET"])
@api_view(["GET"])
def maturityLevel(request:Request):
    """
    Return the maturity level of the project

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response
    :rtype: JSONResponse

    """
    try:
        orgaAsDict = ProfileManagementBase.getOrganization(request.session)
        if isinstance(orgaAsDict, Exception):
            raise ValidationError("No organization found")
        if OrganizationDetailsSKI.maturityLevel in orgaAsDict[OrganizationDescription.details]:
            return Response({OrganizationDetailsSKI.maturityLevel.value: orgaAsDict[OrganizationDescription.details][OrganizationDetailsSKI.maturityLevel]})
        else:
            return Response({OrganizationDetailsSKI.maturityLevel.value: []})
        
    except (Exception) as error:
        message = f"Error in {maturityLevel.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#######################################################

@extend_schema(
    summary="Return the resilience score of the project",
    description=" ",
    tags=['FE - Questionnaire'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["GET"])
@api_view(["GET"])
def resilienceScore(request:Request):
    """
    Return the resilience score of the project

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response
    :rtype: JSONResponse

    """
    try:
        orgaAsDict = ProfileManagementBase.getOrganization(request.session)
        if isinstance(orgaAsDict, Exception):
            raise ValidationError("No organization found")
        if OrganizationDetailsSKI.resilienceScore in orgaAsDict[OrganizationDescription.details]:
            return Response({OrganizationDetailsSKI.resilienceScore.value: orgaAsDict[OrganizationDescription.details][OrganizationDetailsSKI.resilienceScore]})
        else:
            return Response({OrganizationDetailsSKI.resilienceScore.value: []})
    except (Exception) as error:
        message = f"Error in {resilienceScore.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)