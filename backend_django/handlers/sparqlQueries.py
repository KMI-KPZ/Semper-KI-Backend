"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Test handler for sparql
"""

from django.http import JsonResponse

from ..services import cmem

#######################################################
def sendQuery(request):
    """
    Test Sparql queries that come from the form.

    :param request: POST Request
    :type request: HTTP POST
    :return: Json containing results of the query
    :rtype: JSONResponse

    """
    results = cmem.sendQuery(request.POST["query"])
    
    return JsonResponse(results, safe=False)

#######################################################
def sendQuery(request):
    """
    Test Sparql query.

    :param request: GET Request
    :type request: HTTP GET
    :return: Json containing results of testquery
    :rtype: JSONResponse

    """
    results = cmem.sendQuery("SELECT * where {?s ?p ?o} LIMIT 100")
    
    return JsonResponse(results, safe=False)