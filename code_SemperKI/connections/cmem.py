"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for the sparql endpoint
"""

import copy
import re
from django.conf import settings
from SPARQLWrapper import SPARQLWrapper, JSON

from Generic_Backend.code_General.utilities.oauth import ManageToken
from Generic_Backend.code_General.connections.redis import RedisConnection

##################################################################
class ManageSPARQLQuery:
    """
    Contains query from file as object

    """
    
    #######################################################
    def __init__(self, filePathAndName, post=False, parameters={}) -> None:
        """
        Retrieve query from file and save it into redis 

        :param filePathAndName: the very same
        :type filePathAndName: str
        :param post: True if the query posts something, False if it gets something
        :type post: Bool
        :return: Nothing
        :rtype: None
        
        """
        self.redisCon = RedisConnection()
        getEndpoint = SPARQLWrapper(settings.CMEM_SPARQL_ENDPOINT)
        updateEndpoint = SPARQLWrapper(settings.CMEM_SPARQL_UPDATE_ENDPOINT)
        self.oauthToken = ManageToken(settings.CMEM_CLIENT_ID, settings.CMEM_CLIENT_SECRET, token_endpoint=settings.CMEM_TOKEN_ENDPOINT, token_endpoint_auth_method='client_secret_post')

        self.filePathAndName = filePathAndName
        self.parameters = parameters

        if post:
            self.endpoint = updateEndpoint
            self.endpoint.setMethod("POST") # GET is default
        else:
            self.endpoint = getEndpoint

        self.retrieveContentFromRedis(initial=True) # save file initially

    #######################################################
    def retrieveContentFromRedis(self, initial=False) -> str:
        """
        Check if the key is inside redis, if it is, take it from there, if not, save it for faster access

        :return: The query as string
        :rtype: str

        """
        query, exists = self.redisCon.retrieveContentJSON(self.filePathAndName)
        if not exists or initial:
            with open(str(settings.BASE_DIR) + self.filePathAndName) as queryFile:
                queryFileContent = queryFile.read()
                self.redisCon.addContentJSON(self.filePathAndName, {"content": queryFileContent}, True)
                return queryFileContent
        else:
            return query["content"]
        
    #######################################################
    def getParameters(self) -> dict:
        """
        Retrieve the parameters if there are any so that they can be filled

        :return: Dictionary that describe the parameters for the query
        :rtype: dict

        """
        return copy.deepcopy(self.parameters) # needs to be changeable

    #######################################################
    def sendQuery(self, parameters:dict={}):
        """
        Send SPARQL query.
        :param self: Contains sparql query as obj
        :type self: Object
        :param parameters: The parameters for the query. Need to come from the outside to ensure thread safety!
        :type parameters: dict
        :return: result of query
        :rtype: JSON

        """
        # retrieve query and set parameters
        query = self.retrieveContentFromRedis()
        for parameter in parameters:
            value = parameters[parameter]
            regexPattern = r"\[\$"+re.escape(parameter) + r"\]"
            query = re.sub(regexPattern, value, query)

        # request a refresh token
        self.oauthToken.checkIfExpired()

        # maybe construct first, save that to redis and then search/filter from that
        endpointCopy = self.endpoint
        endpointCopy.addCustomHttpHeader(
        httpHeaderName="Authorization", httpHeaderValue="Bearer "+self.oauthToken.token["access_token"])
        endpointCopy.setReturnFormat(JSON)
        endpointCopy.setQuery(query)

        results = endpointCopy.queryAndConvert()
        if results == b'':
            return {}
        if "results" in results:
            if "bindings" in results["results"]:
                return results["results"]["bindings"]
            return results["results"]
        return {}
        
    

