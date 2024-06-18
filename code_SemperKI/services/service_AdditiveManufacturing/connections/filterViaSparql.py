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
    if "measurements" in calculations:
        # Calculations:
        # "measurements": {
        #     "volume": -1.0,
        #     "surfaceArea": -1.0,
        #     "mbbDimensions": {
        #         "_1": -1.0,
        #         "_2": -1.0,
        #         "_3": -1.0,
        printers = getPrintersByBuildPlate.sendQuery({
            SparqlParameters.min_height: calculations["measurements"]["mbbDimensions"]["_1"],
            SparqlParameters.min_length: calculations["measurements"]["mbbDimensions"]["_2"],
            SparqlParameters.min_width: calculations["measurements"]["mbbDimensions"]["_3"],
            })

    return []