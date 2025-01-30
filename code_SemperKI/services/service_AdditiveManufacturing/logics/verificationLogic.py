"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Logic for verification
"""

import logging

from rest_framework.request import Request

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase

from code_SemperKI.definitions import *

from ..definitions import *
from ..modelFiles.verificationModel import *
from ..connections.postgresql.pgVerification import * 

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

####################################################################################
def getVerificationForOrganizationLogic(request:Request) -> tuple[list[dict]|Exception, int]:
    """
    Retrieve the current verification for the organization
    
    """
    orgaID = ProfileManagementBase.getOrganizationHashID(request.session)
    if orgaID == "":
        return Exception("Organization not found"), 404
    result = getVerification(orgaID)
    if isinstance(result, Exception):
        return result, 500
    return result, 200

####################################################################################
def createVerificationForOrganizationLogic(request:Request, verifiedInput) -> tuple[dict|Exception, int]:
    """
    Create a new verification
    
    """
    orgaID = ProfileManagementBase.getOrganizationHashID(request.session)
    if orgaID == "":
        return Exception("Organization not found"), 404
    result = createVerification(orgaID, verifiedInput["printerID"], verifiedInput["materialID"], verifiedInput["status"], verifiedInput["details"])
    if isinstance(result, Exception):
        return result, 500
    return result.toDict(), 200

####################################################################################
def updateVerificationForOrganizationLogic(request:Request, verifiedInput) -> tuple[None|Exception, int]:
    """
    Update a verification
    
    """
    orgaID = ProfileManagementBase.getOrganizationHashID(request.session)
    if orgaID == "":
        return Exception("Organization not found"), 404
    result = updateVerification(orgaID, verifiedInput["printerID"], verifiedInput["materialID"], verifiedInput["status"], verifiedInput["details"])
    if isinstance(result, Exception):
        return result, 500
    return None, 200

####################################################################################
def deleteVerificationForOrganizationLogic(request:Request, printerID:str, materialID:str) -> tuple[None|Exception, int]:
    """
    Delete a verification
    
    """
    orgaID = ProfileManagementBase.getOrganizationHashID(request.session)
    if orgaID == "":
        return Exception("Organization not found"), 404
    result = deleteVerification(orgaID, printerID, materialID)
    if isinstance(result, Exception):
        return result, 500
    return None, 200