"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions using the sparql queries to filter for contractors
"""

from ..utilities.sparqlQueries import *

##################################################
def filterByMaterial(resultDict:dict, chosenMaterials:dict):
    """
    Filter by material choice

    :param resultDict: Where the found manufacturers go
    :type resultDict: dict
    :param chosenMaterials: The materials in the serviceDetails
    :type chosenMaterials: dict
    :return: Nothing, result is written in-place
    :rtype: None
    
    """
    manufacturers = getManufacturersByMaterial.sendQuery()
    for entry in manufacturers:
        if entry["ID"]["value"] not in resultDict:
            resultDict[entry["ID"]["value"]] = entry

##################################################
def filterByPostProcessings(resultDict:dict, chosenPostProcessings:dict):
    """
    Filter by post-processings choice

    :param resultDict: Where the found manufacturers go
    :type resultDict: dict
    :param chosenPostProcessings: The post-processings in the serviceDetails
    :type chosenPostProcessings: dict
    :return: Nothing, result is written in-place
    :rtype: None
    
    """
    return None

##################################################
def filterByBuildPlate(resultDict:dict, calculations:dict):
    """
    Filter by dimension of the build plate of the printers

    :param resultDict: Where the found manufacturers go
    :type resultDict: dict
    :param calculations: The calculations in the serviceDetails
    :type calculations: dict
    :return: Nothing, result is written in-place
    :rtype: None
    
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
        manufacturers = getManufacturersByBuildPlate.sendQuery({
            SparqlParameters.min_height: calculations["measurements"]["mbbDimensions"]["_1"],
            SparqlParameters.min_length: calculations["measurements"]["mbbDimensions"]["_2"],
            SparqlParameters.min_width: calculations["measurements"]["mbbDimensions"]["_3"],
            })
        
        for entry in manufacturers:
            if entry["ID"]["value"] not in resultDict:
                resultDict[entry["ID"]["value"]]  = entry