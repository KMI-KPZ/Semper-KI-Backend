"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Calls to ontology for adding and retrieving data
"""

import datetime
import json, requests, logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from ..utilities import mocks

from ..services.postgresDB import pgProfiles
from ..utilities.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, Logging
from django.views.decorators.http import require_http_methods

from ..services import cmem

logger = logging.getLogger("logToFile")

#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def onto_getMaterials(request):
    """
    Gathers all available materials from the knowledge graph/ontology

    :param request: Get request from frontend
    :type request: HTTP GET
    :return: Flat list of Materials
    :rtype: JSONResponse
    """

    resultsOfQueries = {"materials": []}
    materialsRes = cmem.getAllMaterials.sendQuery()
    for elem in materialsRes:
        title = elem["Material"]["value"]
        resultsOfQueries["materials"].append({"title": title, "URI": elem["Material"]["value"]})
        
    return JsonResponse(resultsOfQueries)

#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def onto_getPrinters(request):
    """
    Gathers all available 3D printers from the knowledge graph/ontology

    :param request: Get request from frontend
    :type request: HTTP GET
    :return: Flat list of printers
    :rtype: JSONResponse
    """

    resultsOfQueries = {"printers": []}
    printersRes = cmem.getAllPrinters.sendQuery()
    for elem in printersRes:
        title = elem["Printer"]["value"]
        resultsOfQueries["printers"].append({"title": title, "URI": elem["Printer"]["value"]})
        
    return JsonResponse(resultsOfQueries)


#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def onto_getPrinter(request):
    """
    Gathers info about one specific 3D printer from the knowledge graph/ontology

    :param request: Post request from frontend
    :type request: HTTP POST
    :return: Info about a printer
    :rtype: JSONResponse
    """

    ######### mocked #########

    printerName = json.loads(request.body.decode("utf-8"))["printer"]
    resultsOfQueries = {"properties": []}
    #with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Printer/<>.txt") as printer:
    #    printersRes = cmem.sendQuery(printer.read())
    #    for elem in printersRes:
    #        title = elem["Printer"]["value"]
    #        resultsOfQueries["printer"].append({"title": title, "properties": [], "URI": elem["Printer"]["value"]})
            
    resultsOfQueries["properties"] = mocks.mockPrinter()
    return JsonResponse(resultsOfQueries)


#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def onto_getMaterial(request):
    """
    Gathers info about one specific meterial from the knowledge graph/ontology

    :param request: Post request from frontend
    :type request: HTTP POST
    :return: Info about a material
    :rtype: JSONResponse
    """

    ######### mocked #########

    printerName = json.loads(request.body.decode("utf-8"))["material"]
    resultsOfQueries = {"properties": []}
    #with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Printer/<>.txt") as printer:
    #    printersRes = cmem.sendQuery(printer.read())
    #    for elem in printersRes:
    #        title = elem["Printer"]["value"]
    #        resultsOfQueries["printer"].append({"title": title, "properties": [], "URI": elem["Printer"]["value"]})
            
    resultsOfQueries["properties"] = mocks.mockMaterial()
    return JsonResponse(resultsOfQueries)


##############################################################################################################

#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def orga_getPrinters(request):
    """
    Gathers list of printers assigned to that organization from the knowledge graph/ontology

    :param request: Post request from frontend
    :type request: HTTP POST
    :return: List of printers
    :rtype: JSONResponse
    """

    ######### mocked #########

    orgaName = json.loads(request.body.decode("utf-8"))["organization"]
    resultsOfQueries = {"printers": []}
    printersRes = cmem.getAllPrinters.sendQuery()
    for elem in printersRes:
        title = elem["Printer"]["value"]
        resultsOfQueries["printers"].append({"title": title, "URI": elem["Printer"]["value"]})
    return JsonResponse(resultsOfQueries)

    
#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def orga_addPrinter(request):
    """
    Links an existing printer to that organization in the knowledge graph/ontology

    :param request: Post request from frontend with organization name and printer name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """

    ######### mocked #########

    body = json.loads(request.body.decode("utf-8"))
    orgaName = body["organization"]
    printerName = body["printer"]

    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUser(request.session)['name']},{Logging.Predicate.DEFINED},added,{Logging.Object.OBJECT},printer {printerName} to the ontology," + str(datetime.datetime.now()))
    return HttpResponse("Success", status=200)


#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def orga_addPrinterEdit(request):
    """
    Links an existing printer to that organization in the knowledge graph/ontology and adds some extra info

    :param request: Post request from frontend with organization name and printer name as well as properties
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """

    ######### mocked #########

    body = json.loads(request.body.decode("utf-8"))
    orgaName = body["organization"]
    printerName = body["printer"]
    props = body["properties"]
    
    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUser(request.session)['name']},{Logging.Predicate.EDITED},added/edited,{Logging.Object.OBJECT},printer {printerName} to the ontology," + str(datetime.datetime.now()))
    return HttpResponse("Success", status=200)


#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def orga_createPrinter(request):
    """
    Adds a new printer for that organization to the knowledge graph/ontology

    :param request: Post request from frontend with organization name and printer details
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """

    ######### mocked #########

    body = json.loads(request.body.decode("utf-8"))
    orgaName = body["organization"]
    printerName = body["printer"]
    props = body["properties"]
    
    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUser(request.session)['name']},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},printer {printerName} to the ontology," + str(datetime.datetime.now()))
    return HttpResponse("Success", status=200)


#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def orga_removePrinter(request):
    """
    Unlinks an existing printer of that organization in the knowledge graph/ontology

    :param request: Post request from frontend with organization name and printer name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """

    ######### mocked #########

    body = json.loads(request.body.decode("utf-8"))
    orgaName = body["organization"]
    printerName = body["printer"]
    
    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUser(request.session)['name']},{Logging.Predicate.DELETED},removed,{Logging.Object.OBJECT},printer {printerName} to the ontology," + str(datetime.datetime.now()))
    return HttpResponse("Success", status=200)


#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def orga_addMaterial(request):
    """
    Links an existing material to that organization in the knowledge graph/ontology

    :param request: Post request from frontend with organization name and material name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """

    ######### mocked #########

    body = json.loads(request.body.decode("utf-8"))
    orgaName = body["organization"]
    materialName = body["material"]
    
    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUser(request.session)['name']},{Logging.Predicate.DEFINED},added,{Logging.Object.OBJECT},material {materialName} to the ontology," + str(datetime.datetime.now()))
    return HttpResponse("Success", status=200)

    
#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def orga_addMaterialEdit(request):
    """
    Links an existing material to that organization in the knowledge graph/ontology and adds some custom properties

    :param request: Post request from frontend with organization name and material name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """

    ######### mocked #########

    body = json.loads(request.body.decode("utf-8"))
    orgaName = body["organization"]
    materialName = body["material"]
    props = body["properties"]
    
    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUser(request.session)['name']},{Logging.Predicate.EDITED},added/edited,{Logging.Object.OBJECT},material {materialName} to the ontology," + str(datetime.datetime.now()))
    return HttpResponse("Success", status=200)

#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def orga_createMaterial(request):
    """
    Creates a new material and links it to that organization in the knowledge graph/ontology

    :param request: Post request from frontend with organization name and material name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """

    ######### mocked #########

    body = json.loads(request.body.decode("utf-8"))
    orgaName = body["organization"]
    materialName = body["material"]
    props = body["properties"]
    
    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUser(request.session)['name']},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},material {materialName} to the ontology," + str(datetime.datetime.now()))
    return HttpResponse("Success", status=200)

#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def orga_removeMaterial(request):
    """
    Unlinks an existing material of that organization in the knowledge graph/ontology

    :param request: Post request from frontend with organization name and material name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """

    ######### mocked #########

    body = json.loads(request.body.decode("utf-8"))
    orgaName = body["organization"]
    materialName = body["material"]
    
    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUser(request.session)['name']},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},material {materialName} to the ontology," + str(datetime.datetime.now()))
    return HttpResponse("Success", status=200)


#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["POST"])
@checkIfRightsAreSufficient(json=True)
def orga_getMaterials(request):
    """
    Lists all materials of that organization from the knowledge graph/ontology
    
    :param request: Post request from frontend with organization name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """
    ######### mocked #########

    orgaName = json.loads(request.body.decode("utf-8"))["organization"]
    resultsOfQueries = {"materials": []}
    materialsRes = cmem.getAllMaterials.sendQuery()
    for elem in materialsRes:
        title = elem["Material"]["value"]
        resultsOfQueries["materials"].append({"title": title, "URI": elem["Material"]["value"]})
            
    return JsonResponse(resultsOfQueries)
