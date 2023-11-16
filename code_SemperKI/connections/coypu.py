"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for the sparql endpoint of coypu
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings
import datetime

from .redis import RedisConnection

class ManageQueries:
    """
    Contains query from file as object

    """
    redisCon = RedisConnection()

    #######################################################
    def __init__(self, filePathAndName) -> None:
        self.endpoint = SPARQLWrapper("https://skynet.coypu.org/coypu-internal")
        self.endpoint.setCredentials(settings.COYPU_CLIENTID, settings.COYPU_PASSWORD)

        query, exists = self.redisCon.retrieveContentJSON("coypuQuery")
        if not exists:
            with open(str(settings.BASE_DIR) + filePathAndName) as queryFile:
                queryFileContent = queryFile.read()
                self.redisCon.addContentJSON("coypuQuery", {"coypu": queryFileContent})
                self.savedQuery = queryFileContent
        else:
            self.savedQuery = query["coypu"]

    #######################################################
    def sendQuery(self):
        """
        Send SPARQL query.
        :param self: Contains sparql query as obj
        :type self: Object
        :return: result of query
        :rtype: JSON

        """

        # maybe construct first, save that to redis and then search/filter from that
        endpointCopy = self.endpoint
        endpointCopy.setReturnFormat(JSON)
        endpointCopy.setQuery(self.savedQuery)

        results = endpointCopy.queryAndConvert()
        return results["results"]["bindings"]


########################################
# list of objects
getExampleNews = ManageQueries("/backend_django/SPARQLQueries/Coypu/Example.txt")
