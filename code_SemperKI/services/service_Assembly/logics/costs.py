"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Cost calculations for this service
"""
import math, logging, numpy, sys

from django.conf import settings

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists
from Generic_Backend.code_General.utilities.crypto import encryptObjectWithAES

from code_SemperKI.modelFiles.processModel import ProcessInterface, Process
from code_SemperKI.definitions import *

from ..definitions import *
from ..connections.postgresql import pgKG
from ..connections.filterViaSparql import Filter


logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

# TODO: THIS WHOLE FILE IS A MESS AND NEEDS TO BE REFACTORED

##################################################
PLATFORM_MARGIN = 10. # random value

##################################################
class Costs():
    """
    Calculate all costs associated with the assembly process for one organization
    
    """

    ##################################################
    def __init__(self, process:ProcessInterface|Process, additionalArguments:dict, filterObject:Filter) -> None:
        """
        Gather input variables

        """
        self.processObj = process
        self.additionalArguments = additionalArguments
        self.filterObject = filterObject
        self.detailedCalculations = {} # contains all information about every calculation here, will be encrypted and saved in the process
        ###

    ####################################################################################################
    def calculateCosts(self) -> list[tuple[float,float]]|Exception:
        """
        Calculate all costs
        
        """
        try:
            costsPerGroup = [(0.,0.)]
                
            return costsPerGroup
        except Exception as e:
            loggerError.error("Error in calculateCosts: " + str(e))
            return e
        

    ####################################################################################################
    def getEncryptedCostOverview(self) -> str:
        """
        Encrypt the detailed cost overview
        
        :return: encrypted cost overview as str
        :rtype: str
        """
        return encryptObjectWithAES(settings.AES_ENCRYPTION_KEY,self.detailedCalculations)