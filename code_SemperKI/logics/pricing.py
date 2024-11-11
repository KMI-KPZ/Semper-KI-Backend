"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logics of cost calculation handler
"""

from ..serviceManager import serviceManager

##################################################
def logicOfPriceCalculation(process):
    """
    Calculate the price for every contractor based on the parameters
    
    """

    # TODO calculate costs for manufacturer

    # TODO calculate costs for service
    serviceCosts = serviceManager.getService(process).calculatePriceForService(process, {})
    sumOfServiceCosts = 0.
    for serviceComponent, cost in serviceCosts.values():
        sumOfServiceCosts += cost

    # TODO calculate other costs
    

