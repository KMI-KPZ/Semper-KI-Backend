"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling of frontend filters for models, materials and post processing
"""

import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from ..services import cmem, mocks, crypto

#######################################################
def getProcessData(request):
    """
    Try to filter all according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Models accoding to filters via JSON
    :rtype: JSON

    """
    # get filters set by user
    filters = json.loads(request.body.decode("utf-8"))
    # Filter name is in question -> title, selected stuff is in "answer"
    filtersForSparql = []
    for entry in filters["filters"]:
        filtersForSparql.append([entry["question"]["title"], entry["answer"]])
    #TODO ask via sparql with most general filter and then iteratively filter response
    
    # mockup here:
    filters.update(mocks.modelMock)
    filters.update(mocks.materialMock)
    filters.update(mocks.postProcessingMock)

    # TODO: gzip this 
    return JsonResponse(filters)

#######################################################
def getUploadedModel(files):
    """
    Get uploaded model

    :param files: Saved files from redis
    :type files: array of tuples
    :return: uploaded model
    :rtype: Dictionary

    """
    models = {"models": []}
    for entry in files:
        model = mocks.getEmptyMockModel()
        model["id"] = entry[0]
        model["title"] = entry[1]
        model["URI"] = str(entry[2])
        model["CreatedBy"] = "user"

        models["models"].append(model)
    return model

#######################################################
def getModels(request):
    """
    Try to filter 3d-models according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Models accoding to filters via JSON
    :rtype: JSON

    """
    # get filters set by user
    filters = json.loads(request.body.decode("utf-8"))

    # if user uploaded a file, show that instead
    """     
    response = getUploadedFiles(request.session.session_key) # TODO: select correct model via id
    if response is not None:
        filters.update(getUploadedModel(response))
    else: 
    """
    # Filter name is in question -> title, selected stuff is in "answer"
    filtersForSparql = []
    for entry in filters["filters"]:
        filtersForSparql.append([entry["question"]["title"], entry["answer"]])
    #TODO ask via sparql with most general filter and then iteratively filter response
    
    # mockup here:
    filters.update(mocks.modelMock)
    
    # TODO: gzip this 
    return JsonResponse(filters)

#######################################################
def getMaterials(request):
    """
    Try to filter materials according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Materials accoding to filters via JSON
    :rtype: JSON

    """
    # get filters set by user
    filters = json.loads(request.body.decode("utf-8"))
    # Filter name is in question -> title, selected stuff is in "answer"
    filtersForSparql = []
    for entry in filters["filters"]:
        filtersForSparql.append([entry["question"]["title"], entry["answer"]])
    #TODO ask via sparql with most general filter and then iteratively filter response
    resultsOfQueries = {"materials": []}
    with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Materials/GetAllMaterials.txt") as materials:
        materialsRes = cmem.sendQuery(materials.read())
        for elem in materialsRes:
            title = elem["Material"]["value"]
            resultsOfQueries["materials"].append({"id": crypto.generateMD5(title), "title": title, "propList": [], "URI": mocks.testpicture.mockPicturePath})
    # resultsOfQueries = {"materials": []}
    # with open(str(settings.BASE_DIR) + "/backend_django/SPARQLQueries/Materials/Onto4Add.txt") as onto4AddMaterials:
    #     onto4AddResults = cmem.sendQuery(onto4AddMaterials.read())
    #     for elem in onto4AddResults:
    #         title = elem["s"]["value"].replace("http://www.onto4additive.com/onto4add#","")
    #         resultsOfQueries["materials"].append({"id": crypto.generateMD5(title), "title": title, "propList": [], "URI": mocks.testpicture.mockPicturePath})

    # mockup here:
    #filters.update(mocks.materialMock)
    filters.update(resultsOfQueries)
    
    # TODO: gzip this 
    return JsonResponse(filters)

#######################################################
def getPostProcessing(request):
    """
    Try to filter post processing according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Materials accoding to filters via JSON
    :rtype: JSON

    """
    # get filters set by user
    filters = json.loads(request.body.decode("utf-8"))
    # Filter name is in question -> title, selected stuff is in "answer"
    filtersForSparql = []
    for entry in filters["filters"]:
        filtersForSparql.append([entry["question"]["title"], entry["answer"]])
    #TODO ask via sparql with most general filter and then iteratively filter response

    # mockup here:
    filters.update(mocks.postProcessingMock)
    
    # TODO: gzip this 
    return JsonResponse(filters)

#######################################################
def getFilters(request):
    """
    Try to filter 3d-models according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Models accoding to filters via JSON
    :rtype: JSON

    """
    # get filters set by user
    filters = json.loads(request.body.decode("utf-8"))
    # Filter name is in question -> title, selected stuff is in "answer"
    filtersForSparql = []
    for entry in filters["filters"]:
        filtersForSparql.append([entry["question"]["title"], entry["answer"]])
    #TODO ask via sparql with most general filter and then iteratively filter response
    
    # TODO: gzip this 
    return JsonResponse(filters)