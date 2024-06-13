"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions using the sparql queries to filter for contractors
"""

from ..utilities.sparqlQueries import *

##################################################
def filterByMaterial(chosenMaterials:dict):
    """
    Filter by material choice

    :param chosenMaterials: The materials in the serviceDetails
    :type chosenMaterials: dict
    :return: list of contractors
    :rtype: list
    
    """
    return []

##################################################
def filterByPostProcessings(chosenPostProcessings:dict):
    """
    Filter by post-processings choice

    :param chosenPostProcessings: The post-processings in the serviceDetails
    :type chosenPostProcessings: dict
    :return: list of contractors
    :rtype: list
    
    """
    return []

##################################################
def filterByBuildPlate(calculations:dict):
    """
    Filter by dimension of the build plate of the printers

    :param calculations: The calculations in the serviceDetails
    :type calculations: dict
    :return: list of contractors
    :rtype: list
    
    """
    return []