"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Test handler for sparql
"""

from django.http import JsonResponse

from ..services import cmem

#######################################################
def testQuery(request):
    """
    Test Sparql queries

    :param request: GET Request
    :type request: HTTP GET
    :return: Json containing results of testquery
    :rtype: JSONResponse

    """
    results = cmem.testQuery(request.POST["query"])
    
    return JsonResponse(results, safe=False)