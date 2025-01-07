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

from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderServiceError
import asyncio

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, checkVersion
from Generic_Backend.code_General.utilities import crypto

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
        outList = []
        for entry in services:
            if entry[ServicesStructure.name] == "None":
                continue
            outList.append({"type": entry[ServicesStructure.name], "imgPath": testPicture})
        # NRU ONLY
        outList = outList[:1]
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
        return HttpResponseRedirect(settings.FORWARD_URL)
    except (Exception) as error:
        message = f"Error in {retrieveResultsFromQuestionnaire.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#################################################################################
class DistanceRequestSerializer(serializers.Serializer):
    address1 = serializers.CharField(max_length=255, trim_whitespace=True)
    address2 = serializers.CharField(max_length=255, trim_whitespace=True)

class DistanceResponseSerializer(serializers.Serializer):
    address1 = serializers.CharField(max_length=255)
    coordinates1 = serializers.CharField()
    address2 = serializers.CharField(max_length=255)
    coordinates2 = serializers.CharField()
    distanceKm = serializers.FloatField()

@extend_schema(
    summary="Calculate the geodesic distance between two addresses",
    description=" ",
    request=DistanceRequestSerializer,
    tags=['FE - Miscellaneous'],
    responses={
        200: DistanceResponseSerializer,
        400: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@api_view(["POST"])
def calculateDistanceView(request: Request):
    """
    Calculate the geodesic distance between two addresses.

    :param request: The request object
    :type request: Dict
    :return: The distance between the addresses and their coordinates
    :rtype: JSONResponse
    """
    
    inSerializer = DistanceRequestSerializer(data=request.data)
    if inSerializer.is_valid():
        address1 = inSerializer.data["address1"]
        address2 = inSerializer.data["address2"]
    else:
        return Response({"error": "Both 'address1' and 'address2' must be provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    async def calculateGeodesicDistance(address1, address2):
        async with Nominatim(user_agent="geo_distance_calculator", adapter_factory=AioHTTPAdapter) as geolocator:
            async def fetchCoordinates(address):
                for attempt in range(3):  # Retry up to 3 times
                    try:
                        location = await geolocator.geocode(address, exactly_one=True, timeout=10)
                        if location is None:
                            raise ValueError("Location not found.")
                        return (location.latitude, location.longitude)
                    except GeocoderServiceError:
                        if attempt == 2:  # Last attempt
                            return None
                    except Exception:
                        return None

            coords1 = await fetchCoordinates(address1)
            coords2 = await fetchCoordinates(address2)

            if coords1 and coords2:
                distance = geodesic(coords1, coords2).kilometers
                return {
                    "address1": {
                        "address": address1,
                        "coordinates": coords1
                    },
                    "address2": {
                        "address": address2,
                        "coordinates": coords2
                    },
                    "distanceKm": round(distance, 2)
                }
            else:
                return {"error": "Could not calculate distance due to missing or invalid address data."}

    try:
        
        async def calculateAndRespond():
            result = await calculateGeodesicDistance(address1, address2)

            if "error" in result:
                raise Exception(result["error"])
            
            responseSerializer = DistanceResponseSerializer(data={
                "address1": result["address1"]["address"],
                "coordinates1": str(result["address1"]["coordinates"]),
                "address2": result["address2"]["address"],
                "coordinates2": str(result["address2"]["coordinates"]),
                "distanceKm": result["distanceKm"]
            })

            if not responseSerializer.is_valid():
                raise ValidationError(responseSerializer.errors)
            
            return Response(responseSerializer.data, status=status.HTTP_200_OK)

        return asyncio.run(calculateAndRespond())

    except ValidationError as e:
        errorMessage = {"message": "Validation Error", "exception": str(e)}
        exceptionSerializer = ExceptionSerializer(data=errorMessage)
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
        return Response(errorMessage, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        errorMessage = {"message": "Error in calculateDistanceView", "exception": str(e)}
        exceptionSerializer = ExceptionSerializer(data=errorMessage)
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(errorMessage, status=status.HTTP_500_INTERNAL_SERVER_ERROR)