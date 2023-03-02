from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings

endpoint = SPARQLWrapper("http://host.docker.internal:7200/repositories/cmem")
endpoint.setCredentials(user=settings.SPARQL_USERNAME, passwd=settings.SPARQL_PASSWORD)

#######################################################
def testQuery():
    """
    Test Sparql query.

    :return: result of query
    :rtype: JSON

    """
    # maybe construct first, save that to redis and then search/filter from that
    endpointCopy = endpoint
    endpointCopy.setReturnFormat(JSON)
    endpointCopy.setQuery("""
   SELECT *
   where {?s ?p ?o}
   LIMIT 100
    """)

    results = endpointCopy.queryAndConvert()
    return results["results"]["bindings"]