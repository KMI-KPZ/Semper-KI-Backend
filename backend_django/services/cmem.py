"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for the sparql endpoint
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings

endpoint = SPARQLWrapper("http://host.docker.internal:7200/repositories/cmem")
endpoint.setCredentials(user=settings.SPARQL_USERNAME, passwd=settings.SPARQL_PASSWORD)

#######################################################
def sendQuery(query):
    """
    Send SPARQL query.
    :param query: Contains sparql query as string
    :type query: str
    :return: result of query
    :rtype: JSON

    """
    # maybe construct first, save that to redis and then search/filter from that
    endpointCopy = endpoint
    endpointCopy.setReturnFormat(JSON)
    endpointCopy.setQuery(query)
#     endpointCopy.setQuery("""
#     PREFIX test: <http://www.exampe.org/O4A.owl#>
#     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#        SELECT *
#    where {?s ?p test:Description}
#    LIMIT 100
#     """)
    # SELECT *
   #where {?s ?p ?o}

    results = endpointCopy.queryAndConvert()
    return results["results"]["bindings"]