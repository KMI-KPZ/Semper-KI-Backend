"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Test handler for sparql
"""
import re
from django.http import JsonResponse
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse

from ..services import cmem, coypu

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
def sendQueryCoypu(request):
    """
    Test Sparql for coypu

    :param request: POST Request
    :type request: HTTP POST
    :return: Json containing results of the query
    :rtype: JSONResponse

    """
    results = coypu.getExampleNews.sendQuery()
    pattern = re.compile(".*a class=\"external text\" href=\"(.*)\" rel")
    for idx, element in enumerate(results):
        htmlText = element["rawhtml"]["value"]
        url = ""
        searchResult = pattern.search(htmlText)
        if searchResult != None:
            url = searchResult.group(1)
        results[idx]["rawhtml"]["url"] = url

    
    return JsonResponse(results, safe=False)

#######################################################
def sendTestQuery(request):
    """
    Test Sparql query.

    :param request: GET Request
    :type request: HTTP GET
    :return: Json containing results of testquery
    :rtype: JSONResponse

    """
    results = cmem.sendQuery("SELECT * where {?s ?p ?o} LIMIT 100")
    
    return JsonResponse(results, safe=False)