"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Imports the RAL to hex and name color table
"""

import csv, logging

from django.conf import settings

from Generic_Backend.code_General.connections.redis import RedisConnection

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
def getRALDict():
    """
    Retrieve the RAL color table from the Redis database

    :return: RAL color table
    :rtype: dict
    """
    try:
        redisConn = RedisConnection()
        ralDict = redisConn.retrieveContentJSON("RALTable")
        outDict = {}
        if ralDict[1] is False:
            csvContent = csv.reader(open(str(settings.BASE_DIR) + "/code_SemperKI/services/service_AdditiveManufacturing/ral_classic.csv", "r"), delimiter=",")
            next(csvContent) # skip header
            for row in csvContent:
                outDict[row[0]] = {"RAL": row[0], "de-DE": row[6], "en-EN": row[5], "HEX": row[2]} #TODO: Decide upon a key
            redisConn.addContentJSON("RALTable", outDict)
        else:
            outDict = ralDict[0]
        return outDict
    except Exception as e:
        logger.error("Error in getRALDict: " + str(e))
        return None
