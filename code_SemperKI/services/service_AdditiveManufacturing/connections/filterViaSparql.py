"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions using the sparql queries to filter for contractors
"""

import copy
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
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
    #manufacturers = getManufacturersByMaterial.sendQuery()
    # for entry in manufacturers:
    #     if entry["ID"]["value"] not in resultDict:
    #         resultDict[entry["ID"]["value"]] = entry

    for materialID in chosenMaterials:
        material = pgKnowledgeGraph.getNode(materialID)
        orgas = pgKnowledgeGraph.getSpecificNeighborsByType(material.nodeID, pgKnowledgeGraph.NodeType.organization)
        for orga in orgas:
            resultDict[orga[pgKnowledgeGraph.NodeDescription.nodeID]] = orga
    

##################################################
def filterByPostProcessings(resultDict:dict, chosenPostProcessings:dict):
    """
    Filter by post-processings choice, must be called after filterByMaterial

    :param resultDict: Where the found manufacturers go
    :type resultDict: dict
    :param chosenPostProcessings: The post-processings in the serviceDetails
    :type chosenPostProcessings: dict
    :return: Nothing, result is written in-place
    :rtype: None
    
    """
    tempDict = {}
    for postProcessingID in chosenPostProcessings:
        postProcessing = pgKnowledgeGraph.getNode(postProcessingID)
        orgas = pgKnowledgeGraph.getSpecificNeighborsByType(postProcessing.nodeID, pgKnowledgeGraph.NodeType.organization)
        for orga in orgas:
            tempDict[orga[pgKnowledgeGraph.NodeDescription.nodeID]] = orga
    
    copiedDict = copy.deepcopy(resultDict)
    for alreadyFilteredManufacturer in resultDict:
        if alreadyFilteredManufacturer not in tempDict:
            copiedDict.pop(alreadyFilteredManufacturer)
    resultDict.clear()
    resultDict.update(copiedDict)
            

##################################################
def filterByBuildPlate(resultDict:dict, calculations:dict):
    """
    Filter by dimension of the build plate of the printers, must be called after filterByPostProcessings

    :param resultDict: Where the found manufacturers go
    :type resultDict: dict
    :param calculations: The calculations in the serviceDetails
    :type calculations: dict
    :return: Nothing, result is written in-place
    :rtype: None
    
    """
    manufacturersCollection = {}
    listOfSetsForManufacturers:list[set] = []
    for fileID in calculations:
        calculatedValuesForFile = calculations[fileID]
        if "measurements" in calculatedValuesForFile:
            # Calculations:
            # "measurements": {
            #     "volume": -1.0,
            #     "surfaceArea": -1.0,
            #     "mbbDimensions": {
            #         "_1": -1.0,
            #         "_2": -1.0,
            #         "_3": -1.0,
            # manufacturers = getManufacturersByBuildPlate.sendQuery({
            #     SparqlParameters.min_height: calculations["measurements"]["mbbDimensions"]["_1"],
            #     SparqlParameters.min_length: calculations["measurements"]["mbbDimensions"]["_2"],
            #     SparqlParameters.min_width: calculations["measurements"]["mbbDimensions"]["_3"],
            #     })
            
            # for entry in manufacturers:
            #     if entry["ID"]["value"] not in manufacturersWhichCanDoAll:
            #         manufacturersWhichCanDoAll[entry["ID"]["value"]]  = entry
            setOfManufacturerIDs = set()
            printers = pgKnowledgeGraph.getNodesByProperty(pgKnowledgeGraph.NodeProperties.buildVolume)
            for printer in printers:
                buildVolumeArray = printer[pgKnowledgeGraph.NodeDescription.properties][pgKnowledgeGraph.NodeProperties.buildVolume].split("x")
                if calculatedValuesForFile["measurements"]["mbbDimensions"]["_1"] <= float(buildVolumeArray[0]) and \
                    calculatedValuesForFile["measurements"]["mbbDimensions"]["_2"] <= float(buildVolumeArray[1]) and \
                    calculatedValuesForFile["measurements"]["mbbDimensions"]["_3"] <= float(buildVolumeArray[2]):
                        manufacturers = pgKnowledgeGraph.getSpecificNeighborsByType(printer[pgKnowledgeGraph.NodeDescription.nodeID], pgKnowledgeGraph.NodeType.organization)
                        for manufacturer in manufacturers:
                            setOfManufacturerIDs.add(manufacturer[pgKnowledgeGraph.NodeDescription.nodeID])
                            manufacturersCollection[manufacturer[pgKnowledgeGraph.NodeDescription.nodeID]] = manufacturer
            listOfSetsForManufacturers.append(setOfManufacturerIDs)
    
    if len(listOfSetsForManufacturers) > 0:
        manufacturersWhoCanDoItAll = listOfSetsForManufacturers[0].intersection(*listOfSetsForManufacturers[1:])

        if len(manufacturersWhoCanDoItAll) > 0:
            copiedDict = copy.deepcopy(resultDict)
            for alreadyFilteredManufacturer in resultDict:
                if alreadyFilteredManufacturer not in manufacturersWhoCanDoItAll:
                    copiedDict.pop(alreadyFilteredManufacturer)
            resultDict.clear()
            resultDict.update(copiedDict)
