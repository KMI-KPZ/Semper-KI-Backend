from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings
from django.http import JsonResponse
import os

def testQuery(request):
    """
    Test Sparql queries

    :param request: ?
    :type request: ?
    :return: ?
    :rtype: ?

    """
    # maybe construct first, save that to redis and then search/filter from that
    sparql = SPARQLWrapper("http://host.docker.internal:7200/repositories/cmem")
    sparql.setCredentials(user=os.environ.get("SPARQLUSERNAME"), passwd=os.environ.get("SPARQLPW"))
    sparql.setReturnFormat(JSON)
    sparql.setQuery("""
   SELECT *
   where {?s ?p ?o}
   LIMIT 100
    """)

    results = sparql.queryAndConvert()
    return JsonResponse(results["results"]["bindings"], safe=False)