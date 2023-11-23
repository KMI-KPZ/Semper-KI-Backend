"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for the sparql endpoint
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings
import datetime
from authlib.integrations.requests_client import OAuth2Session

from code_General.connections.redis import RedisConnection

########################################################################
class ManageToken:
    """
    Manage oauth token class.
    """
    _token = None
    client = OAuth2Session(settings.CMEM_CLIENT_ID, settings.CMEM_CLIENT_SECRET,token_endpoint="https://cmem.semper-ki.org/auth/realms/cmem/protocol/openid-connect/token", token_endpoint_auth_method='client_secret_post')

    #######################################################
    def __getattr__(self, item):
        if item == "token":
            if self._token is None:
                self.getAccessToken()
            return self._token
        else:
            raise AttributeError
    
    #######################################################
    def __del__(self):
        self.client.close()

    #######################################################
    def getAccessToken(self):
        """
        Get initial token. Made as a function to be callable from outside. 
        Reminder for me: It makes no sense to save this access token in redis because it expires much to quickly!
        """
        self._token = self.client.fetch_token(grant_type='client_credentials')
    
    #######################################################
    def checkIfExpired(self):
        """
        Check if token has expired and if so, refresh it. 
        """
        expirationTimeAT = str(datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=self.token["expires_at"]))
        expirationTimeRT = str(datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=self.token["expires_at"]-self.token["expires_in"]+self.token["refresh_expires_in"]))
        if datetime.datetime.now() > datetime.datetime.strptime(expirationTimeAT,"%Y-%m-%d %H:%M:%S+00:00"):
            # check if refresh token has expired as well
            if datetime.datetime.now() > datetime.datetime.strptime(expirationTimeRT,"%Y-%m-%d %H:%M:%S+00:00"):
                # it has, request new token
                self.getAccessToken()
            else:
                # it has not, ask for refresh token
                self.token = self.client.refresh_token("https://cmem.semper-ki.org/auth/realms/cmem/protocol/openid-connect/token", refresh_token=self.token["refresh_token"])

endpoint = SPARQLWrapper("https://cmem.semper-ki.org/dataplatform/proxy/default/sparql")
oauthToken = ManageToken()

##################################################################
class ManageQueries:
    """
    Contains query from file as object

    """
    redisCon = RedisConnection()

    #######################################################
    def __init__(self, filePathAndName) -> None:

        query, exists = self.redisCon.retrieveContentJSON(filePathAndName)
        if not exists:
            with open(str(settings.BASE_DIR) + filePathAndName) as queryFile:
                queryFileContent = queryFile.read()
                self.redisCon.addContentJSON(filePathAndName, {"content": queryFileContent})
                self.savedQuery = queryFileContent
        else:
            self.savedQuery = query["content"]

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
        endpointCopy.setQuery(self.savedQuery)

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


#######################################################
# import from other services
import services.code_service_AdditiveManufacturing.connections.cmem 