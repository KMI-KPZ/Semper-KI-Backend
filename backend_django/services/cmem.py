"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for the sparql endpoint
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings
import requests
"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for oauth verification
"""

#######################################################
def get_access_token(url, client_id, client_secret):
    """
    Get access token from cmem
    :param url: Url where to get the token from
    :type url: str
    :param client_id: Client ID from settings/env
    :type client_id: str
    :param client_secret: Client Secret from settings/env
    :type client_secret: str
    :return: Access token as bearer from cmem
    :rtype: JSON

    """
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    return response.json()["access_token"]

endpoint = SPARQLWrapper("https://cmem.semper-ki.org/dataplatform/proxy/default/sparql")
endpoint.addCustomHttpHeader(
    httpHeaderName="Authorization", httpHeaderValue="Bearer "
    +get_access_token("https://cmem.semper-ki.org/auth/realms/cmem/protocol/openid-connect/token",
                       settings.CMEM_CLIENT_ID, settings.CMEM_CLIENT_SECRET))


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