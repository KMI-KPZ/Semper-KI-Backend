"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions using the sparql queries to filter for contractors
"""

import copy
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertyDescription

from ..connections.postgresql import pgKG
from ..definitions import NodeTypesAM
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

    # they must have all selected materials
    listOfSetsForManufacturers:list[set] = [] 

    for materialID in chosenMaterials:
        setOfManufacturerIDs = set()
        material = pgKnowledgeGraph.Basics.getNode(materialID)
        nodesWithTheSameUID = pgKnowledgeGraph.Basics.getAllNodesThatShareTheUniqueID(material.uniqueID)
        # filter for those of orgas and retrieve the orgaID
        for entry in nodesWithTheSameUID:
            if entry[NodeDescription.createdBy] != pgKnowledgeGraph.defaultOwner:
                setOfManufacturerIDs.add(entry[NodeDescription.createdBy])
        
        listOfSetsForManufacturers.append(setOfManufacturerIDs)
    
    if len(listOfSetsForManufacturers) > 0:
        manufacturersWhoCanDoItAll = listOfSetsForManufacturers[0].intersection(*listOfSetsForManufacturers[1:])

        if len(manufacturersWhoCanDoItAll) > 0:
            if len(resultDict) > 0:
                copiedDict = copy.deepcopy(resultDict)
                for alreadyFilteredManufacturer in resultDict:
                    if alreadyFilteredManufacturer not in manufacturersWhoCanDoItAll:
                        copiedDict.pop(alreadyFilteredManufacturer)
                resultDict.clear()
                resultDict.update(copiedDict)
            else:
                for manufacturer in manufacturersWhoCanDoItAll:
                    resultDict[manufacturer] = manufacturer
            
    

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
    listOfSetsForManufacturers:list[set] = [] 

    for postProcessingID in chosenPostProcessings:
        setOfManufacturerIDs = set()
        postProcessing = pgKnowledgeGraph.Basics.getNode(postProcessingID)
        nodesWithTheSameUID = pgKnowledgeGraph.Basics.getAllNodesThatShareTheUniqueID(postProcessing.uniqueID)
        # filter for those of orgas and retrieve the orgaID
        for entry in nodesWithTheSameUID:
            if entry[NodeDescription.createdBy] != pgKnowledgeGraph.defaultOwner:
                setOfManufacturerIDs.add(entry[NodeDescription.createdBy])
        
        listOfSetsForManufacturers.append(setOfManufacturerIDs)
    
    if len(listOfSetsForManufacturers) > 0:
        manufacturersWhoCanDoItAll = listOfSetsForManufacturers[0].intersection(*listOfSetsForManufacturers[1:])

        if len(manufacturersWhoCanDoItAll) > 0:
            if len(resultDict) > 0:
                copiedDict = copy.deepcopy(resultDict)
                for alreadyFilteredManufacturer in resultDict:
                    if alreadyFilteredManufacturer not in manufacturersWhoCanDoItAll:
                        copiedDict.pop(alreadyFilteredManufacturer)
                resultDict.clear()
                resultDict.update(copiedDict)
            else:
                for manufacturer in manufacturersWhoCanDoItAll:
                    resultDict[manufacturer] = manufacturer
            

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
            setOfManufacturerIDs = pgKG.LogicAM.checkBuildVolume([calculatedValuesForFile["measurements"]["mbbDimensions"]["_1"],calculatedValuesForFile["measurements"]["mbbDimensions"]["_2"],calculatedValuesForFile["measurements"]["mbbDimensions"]["_3"]])
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
