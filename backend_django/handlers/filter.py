import json, base64
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from .files import getUploadedFiles
from ..services import cmem, mocks

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
def getUploadedModel(file):
    """
    Get uploaded model

    :return: uploaded model
    :rtype: Dictionary

    """

    models = {"models": []}
    model = mocks.getEmptyMockModel()
    model["id"] = file[0]
    model["title"] = file[1]
    model["URI"] = file[2]

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
    response = getUploadedFiles(request.session.session_key)[0] # TODO: select correct model via id
    if response is not None:
        filters.update(getUploadedModel(response))
    else:
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


    # mockup here:
    filters.update(mocks.materialMock)
    
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