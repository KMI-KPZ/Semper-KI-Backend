import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from ..services import cmem

#######################################################
def getData(request):
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
    
    # mockup here:
    models = {"models": []}
    for i in range(20):
        models["models"].append(
            {"name": "testmodel", "tags": ["test", "test", "test"], "date": "2023-02-01", "license": "MIT", "certificate": ["None"], "URI": "https://i0.wp.com/letsprint3d.net/wp-content/uploads/2017/04/benchy.jpg?resize=663%2C373&ssl=1"}
        )
    filters.update(models)
    
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
    
    
    return JsonResponse(filters)