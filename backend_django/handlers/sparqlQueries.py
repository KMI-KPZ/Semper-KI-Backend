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
    results = cmem.testQuery()
    
    return JsonResponse(results, safe=False)