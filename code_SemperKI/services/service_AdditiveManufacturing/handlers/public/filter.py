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

from ...definitions import NodeTypesAM

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
                     "values":[{"name": entry[pgKnowledgeGraph.NodeDescription.nodeName], "id": entry[pgKnowledgeGraph.NodeDescription.uniqueID]} for entry in pgKnowledgeGraph.Basics.getNodesByType(NodeTypesAM.materialCategory) if entry[pgKnowledgeGraph.NodeDescription.createdBy] == pgKnowledgeGraph.defaultOwner],
                     "units":None
                     },
                "answer":None
                }
                #,
                #{"id":1,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"deliverTime","category":"GENERAL","type":"SLIDERSELECTION","range":[0,99],"values":None,"units":["Tage","Wochen"]},"answer":None},{"id":2,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"amount","category":"GENERAL","type":"SLIDER","range":[0,99999],"values":None,"units":"Stück"},"answer":None},{"id":3,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"categorys","category":"GENERAL","type":"MULTISELECTION","range":None,"values":["medicine","fashion","hobby","tools","MODELs","toy","gadgets","art","learning"],"units":None},"answer":None},{"id":4,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"boxSize","category":"GENERAL","type":"SLIDERSELECTION","range":[0,9999],"values":None,"units":["m","cm","mm"]},"answer":None},{"id":5,"isChecked":True,"isOpen":False,"question":{"isSelectable":True,"title":"materialcategory","category":"GENERAL","type":"MULTISELECTION","range":[0,9999],"values":["Metall","Plastic","Ceramic","Organic"],"units":None},"answer":{"unit":None,"value":["Plastic"]}},{"id":6,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"volume","category":"MODEL","type":"SLIDERSELECTION","range":[0,9999],"values":None,"units":["m³","cm³","mm³"]},"answer":None},{"id":7,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"materialCategory","category":"MATERIAL","type":"SELECTION","range":None,"values":["plastic","metal","ceramic","organic"],"units":None},"answer":None},{"id":8,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"proceeding","category":"MATERIAL","type":"SELECTION","range":None,"values":["3D-Print,Molding"],"units":None},"answer":None},{"id":9,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"proceeding","category":"PROCEEDING","type":"SELECTION","range":None,"values":["3D-Print","Molding"],"units":None},"answer":None},{"id":10,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"manufacturer","category":"MANUFACTURER","type":"SELECTION","range":None,"values":["Man 1","Man 2"],"units":None},"answer":None},{"id":11,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"postProcessing","category":"POSTPROCESSING","type":"SELECTION","range":None,"values":["Finish","Threds"],"units":None},"answer":None},{"id":12,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"date","category":"TEST","type":"DATE","range":None,"values":None,"units":None},"answer":None},{"id":13,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"text","category":"TEST","type":"TEXT","range":None,"values":None,"units":None},"answer":None},{"id":14,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"textarea","category":"TEST","type":"TEXTAREA","range":None,"values":None,"units":None},"answer":None},{"id":15,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"color","category":"TEST","type":"COLOR","range":None,"values":None,"units":None},"answer":None},{"id":16,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"number","category":"TEST","type":"NUMBER","range":None,"values":None,"units":None},"answer":None},{"id":17,"isChecked":False,"isOpen":False,"question":{"isSelectable":True,"title":"multiselection","category":"TEST","type":"MULTISELECTION","range":None,"values":["medicine","fashion","hobby","tools","MODELs","toy","gadgets","art","learning"],"units":None},"answer":None}]}
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