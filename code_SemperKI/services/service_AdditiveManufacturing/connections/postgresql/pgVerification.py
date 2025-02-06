"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Access for verification model
"""

import logging

from Generic_Backend.code_General.definitions import *

from code_SemperKI.definitions import *

from ...definitions import *
from ...modelFiles.verificationModel import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
####################################################################################
def getVerificationObject(orgaHashID:str, printerID:str, materialID:str) -> Verification|Exception:
    """
    Retrieve one verification for the organization
    
    """
    try:
        result = Verification.objects.get(organizationID=orgaHashID, printerID=printerID, materialID=materialID)
        return result
    except Verification.DoesNotExist as e:
        #loggerError.error("Verification for organization not found") # expected exception, doesn't need to be logged
        return e
    except Exception as e:
        loggerError.error(f"Error in getVerificationObject: {str(e)}")
        return e
    
####################################################################################
def getVerification(orgaHashID:str) -> list[dict]|Exception:
    """
    Retrieve the current verifications for the organization
    
    """
    try:
        result = Verification.objects.filter(organizationID=orgaHashID)
        return [veri.toDict() for veri in result]
    except Verification.DoesNotExist as e:
        loggerError.error("Verification for organization not found")
        return e

####################################################################################
def createVerification(orgaHashID:str, printerID:str, materialID:str, status:int=0, details:dict={}) -> Verification|Exception:
    """
    Create a new verification

    :param orgaHashID: HashID of the organization
    :type orgaHashID: str
    :param printerID: HashID of the printer
    :type printerID: str
    :param materialID: HashID of the material
    :type materialID: str
    :return: Verification|Exception
    :rtype: Verification|Exception

    """
    try:
        createdObj = Verification.objects.create(organizationID=orgaHashID, printerID=printerID, materialID=materialID, status=status, details=details)
        return createdObj
    except Exception as e:
        loggerError.error(f"Error in createVerification: {str(e)}")
        return e

####################################################################################
def updateVerification(orgaHashID:str, printerID:str, materialID:str, status:int=-1, details:dict={}) -> Verification|Exception:
    """
    Update the verification

    :param orgaHashID: HashID of the organization
    :type orgaHashID: str
    :param status: The status of the verification
    :type status: int
    :param details: The details of the verification
    :type details: dict
    :return: Verification|Exception
    :rtype: Verification|Exception

    """
    try:
        obj = Verification.objects.get(organizationID=orgaHashID, printerID=printerID, materialID=materialID)
        if status != -1:
            obj.status = status
        if details != {}:
            obj.details = details
        obj.save()
        return obj
    except Exception as e:
        loggerError.error(f"Error in updateVerification: {str(e)}")
        return e
    
####################################################################################
def deleteVerification(orgaHashID:str, printerID:str="", materialID:str="") -> None|Exception:
    """
    Delete the verification

    :param orgaHashID: HashID of the organization
    :type orgaHashID: str
    :param printerID: HashID of the printer
    :type printerID: str
    :param materialID: HashID of the material
    :type materialID: str
    :return: None|Exception
    :rtype: None|Exception

    """
    try:
        obj = Verification.objects.get(organizationID=orgaHashID, printerID=printerID, materialID=materialID)
        obj.delete()
    except Exception as e:
        loggerError.error(f"Error in deleteVerification: {str(e)}")
        return e