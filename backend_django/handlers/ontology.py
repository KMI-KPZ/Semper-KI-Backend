"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Calls to ontology for adding and retrieving data
"""

import json, requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from ..services import cmem

#######################################################
def onto_getMaterials(request):
    """
    Gathers all available materials from the knowledge graph/ontology
    :param request: Get request from frontend
    :type request: HTTP GET
    :return: Flat list of Materials
    :rtype: JSONResponse
    """

    resultsOfQueries = {"materials": []}
    with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Materials/GetAllMaterials.txt") as materials:
        materialsRes = cmem.sendQuery(materials.read())
        for elem in materialsRes:
            title = elem["Material"]["value"]
            resultsOfQueries["materials"].append({"title": title, "URI": elem["Material"]["value"]})
            
    return JsonResponse(resultsOfQueries)

#######################################################
def onto_getPrinters(request):
    """
    Gathers all available 3D printers from the knowledge graph/ontology
    :param request: Get request from frontend
    :type request: HTTP GET
    :return: Flat list of printers
    :rtype: JSONResponse
    """
    resultsOfQueries = {"printers": []}
    with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Printer/GetAll3DPrinters.txt") as printers:
        printersRes = cmem.sendQuery(printers.read())
        for elem in printersRes:
            title = elem["Printer"]["value"]
            resultsOfQueries["printers"].append({"title": title, "URI": elem["Printer"]["value"]})
            
    return JsonResponse(resultsOfQueries)

#######################################################
def onto_getPrinter(request):
    """
    Gathers info about one specific 3D printer from the knowledge graph/ontology
    :param request: Get request from frontend
    :type request: HTTP GET
    :return: Flat list of Materials
    :rtype: JSONResponse
    """
    resultsOfQueries = {"printer": []}
    with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Printer/GetSpecificPrinterDetails.txt") as printer:
        printersRes = cmem.sendQuery(printer.read())
        for elem in printersRes:
            title = elem["Printer"]["value"]
            resultsOfQueries["printer"].append({"title": title, "properties": {}, "URI": elem["Printer"]["value"]})
            
    return JsonResponse(resultsOfQueries)