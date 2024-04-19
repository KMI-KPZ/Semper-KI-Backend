"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for the sparql endpoint
"""

from django.conf import settings
from SPARQLWrapper import SPARQLWrapper, JSON

from Generic_Backend.code_General.utilities.oauth import ManageToken
from Generic_Backend.code_General.connections.redis import RedisConnection

endpoint = SPARQLWrapper(settings.CMEM_SPARQL_ENDPOINT)
updateEndpoint = SPARQLWrapper(settings.CMEM_SPARQL_UPDATE_ENDPOINT)
oauthToken = ManageToken(settings.CMEM_CLIENT_ID, settings.CMEM_CLIENT_SECRET, token_endpoint=settings.CMEM_TOKEN_ENDPOINT, token_endpoint_auth_method='client_secret_post')

##################################################################
class ManageQueries:
    """
    Contains query from file as object

    """
    redisCon = RedisConnection()

    #######################################################
    def retrieveContentFromRedis(self) -> str:
        """
        Check if the key is inside redis, if it is, take it from there, if not, save it for faster access

        :return: The query as string
        :rtype: str

        """

        query, exists = self.redisCon.retrieveContentJSON(self.filePathAndName)
        if not exists:
            with open(str(settings.BASE_DIR) + self.filePathAndName) as queryFile:
                queryFileContent = queryFile.read()
                self.redisCon.addContentJSON(self.filePathAndName, {"content": queryFileContent}, True)
                return queryFileContent
        else:
            return query["content"]

    #######################################################
    def __init__(self, filePathAndName) -> None:
        """
        Retrieve query from file and save it into redis 

        :param filePathAndName: the very same
        :type filePathAndName: str
        :return: Nothing
        :rtype: None
        
        """
        self.filePathAndName = filePathAndName
        self.retrieveContentFromRedis() # save file initially

    #######################################################
    def sendQuery(self):
        """
        Send SPARQL query.
        :param self: Contains sparql query as obj
        :type self: Object
        :return: result of query
        :rtype: JSON

        """
        # request a refresh token
        oauthToken.checkIfExpired()

        # maybe construct first, save that to redis and then search/filter from that
        endpointCopy = endpoint
        endpointCopy.addCustomHttpHeader(
        httpHeaderName="Authorization", httpHeaderValue="Bearer "+oauthToken.token["access_token"])
        endpointCopy.setReturnFormat(JSON)
        endpointCopy.setQuery(self.retrieveContentFromRedis())

        results = endpointCopy.queryAndConvert()
        return results["results"]["bindings"]


#######################################################
def sendGeneralQuery(query):
    """
    Send SPARQL query.
    :param query: Contains sparql query as string
    :type query: str
    :return: result of query
    :rtype: JSON

    """
    # request a refresh token
    oauthToken.checkIfExpired()

    # maybe construct first, save that to redis and then search/filter from that
    endpointCopy = endpoint
    endpointCopy.addCustomHttpHeader(
    httpHeaderName="Authorization", httpHeaderValue="Bearer "+oauthToken.token["access_token"])
    endpointCopy.setReturnFormat(JSON)
    endpointCopy.setQuery(query)

    results = endpointCopy.queryAndConvert()
    return results["results"]["bindings"]