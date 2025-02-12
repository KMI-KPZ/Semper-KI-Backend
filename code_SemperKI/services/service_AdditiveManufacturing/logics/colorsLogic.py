"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Logic for handlers for color-specific requests
"""

import json, logging, copy

from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase

from ..utilities.colorsUtils import getRALDict

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
def logicForGetRALList(request):
    """
    Get the RAL table and convert to frontend format

    :return: 
    :rtype: dict

    """
    try:
        # get user locale
        userLocale = ProfileManagementBase.getUserLocale(request.session)

        outList = []
        ralDict = getRALDict()
        for entry in ralDict:
            if userLocale == "de-DE":
                outList.append({"RAL": ralDict[entry]["RAL"], "RALName": ralDict[entry]["de-DE"], "Hex": ralDict[entry]["HEX"]})
            else:
                outList.append({"RAL": ralDict[entry]["RAL"], "RALName": ralDict[entry]["en-EN"], "Hex": ralDict[entry]["HEX"]})
        return outList
    except Exception as e:
        logger.error("Error in logicForGetRALList: " + str(e))
        return []