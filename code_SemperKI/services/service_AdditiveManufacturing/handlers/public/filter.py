"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Handlers of frontend filters for AM service details
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
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.serializer import ExceptionSerializer
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph

from ...definitions import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
# TODO serializers
#######################################################
@extend_schema(
    summary="Retrieve the filters used for this service",
    description=" ",
    tags=['FE - AM Filter'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
@require_http_methods(["GET"])
@api_view(["GET"])
@checkVersion(0.3)
def getFilters(request:Request):
    """
    Retrieve the filters used for this service

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response
    :rtype: JSONResponse

    """
    try:
        allMaterialCategories = [{"name": entry[pgKnowledgeGraph.NodeDescription.nodeName], "id": entry[pgKnowledgeGraph.NodeDescription.uniqueID]} for entry in pgKnowledgeGraph.Basics.getNodesByType(NodeTypesAM.materialCategory) if entry[pgKnowledgeGraph.NodeDescription.createdBy] == pgKnowledgeGraph.defaultOwner]
        allMaterials = pgKnowledgeGraph.Basics.getNodesByType(NodeTypesAM.material)
        minTensileStrengthRange = 9999
        maxTensileStrengthRange = 0
        minDensityRange = 9999
        maxDensityRange = 0
        minElongationAtBreak = 100
        maxElongationAtBreak = 0
        setOfCertificates = set()
        for material in allMaterials:
            for prop in material[pgKnowledgeGraph.NodeDescription.properties]:
                if prop[pgKnowledgeGraph.NodePropertyDescription.name] == NodePropertiesAMMaterial.ultimateTensileStrength:
                    propValue = float(prop[pgKnowledgeGraph.NodePropertyDescription.value])
                    if minTensileStrengthRange > propValue:
                        minTensileStrengthRange = propValue
                    if maxTensileStrengthRange < propValue:
                        maxTensileStrengthRange = propValue
                elif prop[pgKnowledgeGraph.NodePropertyDescription.name] == NodePropertiesAMMaterial.density:
                    propValue = float(prop[pgKnowledgeGraph.NodePropertyDescription.value])
                    if minDensityRange > propValue:
                        minDensityRange = propValue
                    if maxDensityRange < propValue:
                        maxDensityRange = propValue
                elif prop[pgKnowledgeGraph.NodePropertyDescription.name] == NodePropertiesAMMaterial.elongationAtBreak:
                    propValue = float(prop[pgKnowledgeGraph.NodePropertyDescription.value])
                    if minElongationAtBreak > propValue:
                        minElongationAtBreak = propValue
                    if maxElongationAtBreak < propValue:
                        maxElongationAtBreak = propValue
                elif prop[pgKnowledgeGraph.NodePropertyDescription.name] == NodePropertiesAMMaterial.certificates:
                    propValues = prop[pgKnowledgeGraph.NodePropertyDescription.value].split(",")
                    setOfCertificates.update(propValues)
        
        tensileStrengthRange = [minTensileStrengthRange, maxTensileStrengthRange]
        densityRange = [minDensityRange, maxDensityRange]
        elongationAtBreakRange = [minElongationAtBreak, maxElongationAtBreak]
        certificateList = list(setOfCertificates)
        filters = {
            "filters": [
                # {"id":0,
                #  "isChecked":False,
                #  "isOpen":False,
                #  "question":{
                #      "isSelectable":True,
                #      "title":"costs",
                #      "category":"GENERAL",
                #      "type":"SLIDER",
                #      "range":[0,9999],
                #      "values":None,
                #      "units":"€"
                #     },
                # "answer":None
                # },
                {"id":0,
                 "isChecked":False,
                 "isOpen":False,
                 "question":{
                     "isSelectable":True,
                     "title":"materialCategory", # TODO define somewhere
                     "category":"MATERIAL", # TODO define somewhere
                     "type":"SELECTION", # TODO define somewhere
                     "range":None,
                     "values":allMaterialCategories,
                     "units":None
                     },
                "answer":None
                },
                {"id":1,
                 "isChecked":False,
                 "isOpen":False,
                 "question":{
                     "isSelectable":True,
                     "title":"tensileStrength",
                     "category":"MATERIAL",
                     "type":"SLIDER",
                     "range":tensileStrengthRange,
                     "values":None,
                     "units":"MPa"
                    },
                "answer":None
                },
                {"id":2,
                 "isChecked":False,
                 "isOpen":False,
                 "question":{
                     "isSelectable":True,
                     "title":"density",
                     "category":"MATERIAL",
                     "type":"SLIDER",
                     "range":densityRange,
                     "values":None,
                     "units":"g/cm³"
                    },
                "answer":None
                },
                {"id":3,
                 "isChecked":False,
                 "isOpen":False,
                 "question":{
                     "isSelectable":True,
                     "title":"elongationAtBreak",
                     "category":"MATERIAL",
                     "type":"SLIDER",
                     "range":elongationAtBreakRange,
                     "values":None,
                     "units":"%"
                    },
                "answer":None
                },
                {"id":4,
                 "isChecked":False,
                 "isOpen":False,
                 "question":{
                     "isSelectable":True,
                     "title":"certificates",
                     "category":"MATERIAL",
                     "type":"MULTISELECTION",
                     "range":None,
                     "values":certificateList,
                     "units":None
                    },
                "answer":None
                }
            ]
        }
        return Response(filters, status=status.HTTP_200_OK)
    except (Exception) as error:
        message = f"Error in {getFilters.cls.__name__}: {str(error)}"
        exception = str(error)
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)