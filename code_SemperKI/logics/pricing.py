"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logics of cost calculation handler
"""

import logging

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import getNestedValue, checkIfNestedKeyExists

from ..modelFiles.processModel import Process
from ..definitions import *
from ..serviceManager import serviceManager

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

##################################################
def logicOfPriceCalculation(process:Process, contractorID:str, additionalArguments:dict):
    """
    Calculate the price for every contractor based on the parameters
    
    """
    try:
        # TODO sanitize the input
        if ProcessDetails.generalInputParameters not in process.processDetails:
            raise Exception("No general input parameters available")
        if ProcessDetails.inputParametersNoModel in process.processDetails:
            # gather parameters
            pass
        else:
            # gather parameters from model files
            pass

        # TODO Do stuff for all model files

        # TODO get parameters from organization
        organization = pgProfiles.ProfileManagementOrganization.getOrganization(hashedID=contractorID)
        if isinstance(organization, Exception):
            raise organization
        if checkIfNestedKeyExists(organization, [OrganizationDescription.details, OrganizationDetails.services, process.serviceType]) is True:
            organizationParameters = organization[OrganizationDescription.details][OrganizationDetails.services][process.serviceType]
        else:
            raise Exception("Service not available for this organization")
        
        # TODO calculate costs for service
        serviceCosts = serviceManager.getService(process.serviceType).calculatePriceForService(process, {})
        sumOfServiceCosts = 0.
        for serviceComponent, cost in serviceCosts.values():
            sumOfServiceCosts += cost

        # TODO calculate other costs
    except Exception as e:
        loggerError.error("Error in logicOfPriceCalculation: " + str(e))
        return e
    

