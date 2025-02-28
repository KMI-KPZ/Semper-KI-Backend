"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Logic for handlers for color-specific requests
"""

import json, logging, copy
from datetime import datetime

from Generic_Backend.code_General.definitions import Logging
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.definitions import ProcessUpdates
from code_SemperKI.logics.processLogics import updateProcessFunction

from ..utilities.colorsUtils import getRALDict
from ..definitions import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
def logicForGetRALList(request) -> list[dict]:
    """
    Get the RAL table and convert to frontend format

    :return: The RAL table in frontend format
    :rtype: list[dict]

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
    
########################################################
def logicForSetColor(request, validatedInput, functionName: str) -> tuple[Exception, int]:
    """
    Set color in the database
    
    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface()
        if interface is None:
            return (Exception(f"Rights not sufficient in {functionName}"), 401)

        groupID = validatedInput["groupID"]
        projectID = validatedInput["projectID"]
        processID = validatedInput["processID"]
        color = validatedInput["color"]

        existingGroups = interface.getProcessObj(projectID, processID).serviceDetails[ServiceDetails.groups]
        updateArray = [{} for i in range(len(existingGroups))]
        updateArray[groupID] = {ServiceDetails.color: color}
        changes = {"changes": {ProcessUpdates.serviceDetails: {ServiceDetails.groups: updateArray}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            return (Exception(f"Rights not sufficient for {functionName}"), 401)
            
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},set,{Logging.Object.OBJECT},color,"+str(datetime.now()))
        
        return (None, 200)
    except Exception as e:
        return (e, 500)
