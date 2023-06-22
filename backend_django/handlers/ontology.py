"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Calls to ontology for adding and retrieving data
"""

import json, requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from ..handlers.basics import checkIfUserIsLoggedIn

from ..services import cmem, mocks

#######################################################
def onto_getMaterials(request):
    """
    Gathers all available materials from the knowledge graph/ontology
    :param request: Get request from frontend
    :type request: HTTP GET
    :return: Flat list of Materials
    :rtype: JSONResponse
    """
    if checkIfUserIsLoggedIn(request):
        resultsOfQueries = {"materials": []}
        with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Materials/GetAllMaterials.txt") as materials:
            materialsRes = cmem.sendQuery(materials.read())
            for elem in materialsRes:
                title = elem["Material"]["value"]
                resultsOfQueries["materials"].append({"title": title, "URI": elem["Material"]["value"]})
                
        return JsonResponse(resultsOfQueries)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def onto_getPrinters(request):
    """
    Gathers all available 3D printers from the knowledge graph/ontology
    :param request: Get request from frontend
    :type request: HTTP GET
    :return: Flat list of printers
    :rtype: JSONResponse
    """
    if checkIfUserIsLoggedIn(request):
        resultsOfQueries = {"printers": []}
        with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Printer/GetAll3DPrinters.txt") as printers:
            printersRes = cmem.sendQuery(printers.read())
            for elem in printersRes:
                title = elem["Printer"]["value"]
                resultsOfQueries["printers"].append({"title": title, "URI": elem["Printer"]["value"]})
                
        return JsonResponse(resultsOfQueries)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def onto_getPrinter(request):
    """
    Gathers info about one specific 3D printer from the knowledge graph/ontology
    :param request: Post request from frontend
    :type request: HTTP POST
    :return: Info about a printer
    :rtype: JSONResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            printerName = json.loads(request.body.decode("utf-8"))["printer"]
            resultsOfQueries = {"properties": []}
            #with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Printer/<>.txt") as printer:
            #    printersRes = cmem.sendQuery(printer.read())
            #    for elem in printersRes:
            #        title = elem["Printer"]["value"]
            #        resultsOfQueries["printer"].append({"title": title, "properties": [], "URI": elem["Printer"]["value"]})
                    
            resultsOfQueries["properties"] = mocks.mockPrinter()
            return JsonResponse(resultsOfQueries)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def onto_getMaterial(request):
    """
    Gathers info about one specific meterial from the knowledge graph/ontology
    :param request: Post request from frontend
    :type request: HTTP POST
    :return: Info about a material
    :rtype: JSONResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            printerName = json.loads(request.body.decode("utf-8"))["material"]
            resultsOfQueries = {"properties": []}
            #with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Printer/<>.txt") as printer:
            #    printersRes = cmem.sendQuery(printer.read())
            #    for elem in printersRes:
            #        title = elem["Printer"]["value"]
            #        resultsOfQueries["printer"].append({"title": title, "properties": [], "URI": elem["Printer"]["value"]})
                    
            resultsOfQueries["properties"] = mocks.mockMaterial()
            return JsonResponse(resultsOfQueries)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)

##############################################################################################################

#######################################################
def orga_getPrinters(request):
    """
    Gathers list of printers assigned to that organization from the knowledge graph/ontology
    :param request: Post request from frontend
    :type request: HTTP POST
    :return: List of printers
    :rtype: JSONResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            orgaName = json.loads(request.body.decode("utf-8"))["organization"]
            resultsOfQueries = {"printers": []}
            with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Printer/GetAll3DPrinters.txt") as printers:
                printersRes = cmem.sendQuery(printers.read())
                for elem in printersRes:
                    title = elem["Printer"]["value"]
                    resultsOfQueries["printers"].append({"title": title, "URI": elem["Printer"]["value"]})
            return JsonResponse(resultsOfQueries)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)
    
#######################################################
def orga_addPrinter(request):
    """
    Links an existing printer to that organization in the knowledge graph/ontology
    :param request: Post request from frontend with organization name and printer name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            body = json.loads(request.body.decode("utf-8"))
            orgaName = body["organization"]
            printerName = body["printer"]
            
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def orga_addPrinterEdit(request):
    """
    Links an existing printer to that organization in the knowledge graph/ontology and adds some extra info
    :param request: Post request from frontend with organization name and printer name as well as properties
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            body = json.loads(request.body.decode("utf-8"))
            orgaName = body["organization"]
            printerName = body["printer"]
            props = body["properties"]
            
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def orga_createPrinter(request):
    """
    Adds a new printer for that organization to the knowledge graph/ontology
    :param request: Post request from frontend with organization name and printer details
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            body = json.loads(request.body.decode("utf-8"))
            orgaName = body["organization"]
            printerName = body["printer"]
            props = body["properties"]
            
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def orga_removePrinter(request):
    """
    Unlinks an existing printer of that organization in the knowledge graph/ontology
    :param request: Post request from frontend with organization name and printer name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            body = json.loads(request.body.decode("utf-8"))
            orgaName = body["organization"]
            printerName = body["printer"]
            
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def orga_addMaterial(request):
    """
    Links an existing material to that organization in the knowledge graph/ontology
    :param request: Post request from frontend with organization name and material name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            body = json.loads(request.body.decode("utf-8"))
            orgaName = body["organization"]
            materialName = body["material"]
            
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)
    
#######################################################
def orga_addMaterialEdit(request):
    """
    Links an existing material to that organization in the knowledge graph/ontology and adds some custom properties
    :param request: Post request from frontend with organization name and material name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            body = json.loads(request.body.decode("utf-8"))
            orgaName = body["organization"]
            materialName = body["material"]
            props = body["properties"]
            
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def orga_createMaterial(request):
    """
    Creates a new material and links it to that organization in the knowledge graph/ontology
    :param request: Post request from frontend with organization name and material name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            body = json.loads(request.body.decode("utf-8"))
            orgaName = body["organization"]
            materialName = body["material"]
            props = body["properties"]
            
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def orga_removeMaterial(request):
    """
    Unlinks an existing material of that organization in the knowledge graph/ontology
    :param request: Post request from frontend with organization name and material name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            body = json.loads(request.body.decode("utf-8"))
            orgaName = body["organization"]
            materialName = body["material"]
            
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)

#######################################################
def orga_getMaterials(request):
    """
    Lists all materials of that organization from the knowledge graph/ontology
    :param request: Post request from frontend with organization name
    :type request: HTTP POST
    :return: Success or not
    :rtype: HTTPResponse
    """
    ######### mocked #########
    if checkIfUserIsLoggedIn(request):
        if request.method == "POST":
            orgaName = json.loads(request.body.decode("utf-8"))["organization"]
            resultsOfQueries = {"materials": []}
            with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Materials/GetAllMaterials.txt") as materials:
                materialsRes = cmem.sendQuery(materials.read())
                for elem in materialsRes:
                    title = elem["Material"]["value"]
                    resultsOfQueries["materials"].append({"title": title, "URI": elem["Material"]["value"]})
                    
            return JsonResponse(resultsOfQueries)
        else:
            return HttpResponse("Wrong method", status=405)
    else:
        return HttpResponse("Not logged in", status=401)