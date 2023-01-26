from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings
from django.http import JsonResponse

def testQuery(request):
    """
    Test Sparql queries

    :param request: ?
    :type request: ?
    :return: ?
    :rtype: ?

    """

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    sparql.setQuery("""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX sdo: <https://schema.org/>

    CONSTRUCT {
      ?lang a sdo:Language ;
      sdo:alternateName ?iso6391Code .
    }
    WHERE {
      ?lang a dbo:Language ;
      dbo:iso6391Code ?iso6391Code .
      FILTER (STRLEN(?iso6391Code)=2) # to filter out non-valid values
    }
    LIMIT 3
    """)

    results = sparql.queryAndConvert()
    return JsonResponse(results["results"]["bindings"])