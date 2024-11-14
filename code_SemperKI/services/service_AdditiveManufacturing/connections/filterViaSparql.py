"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions using the sparql queries to filter for contractors
"""

import copy, logging
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertyDescription

from ..connections.postgresql import pgKG
from ..definitions import *
from ..utilities.sparqlQueries import *

loggerError = logging.getLogger("errors")


##################################################
class Filter():
    """
    Filter and save results
    
    """

    ##################################################
    def __init__(self):
        """
        Init stuff
        
        """
        self.resultDict = {}
        self.printerDict = {}

    ##################################################
    def filterByMaterial(self, chosenMaterials:dict) -> None|Exception:
        """
        Filter by material choice

        :param resultDict: Where the found manufacturers go
        :type resultDict: dict
        :param chosenMaterials: The materials in the serviceDetails
        :type chosenMaterials: dict
        :return: Nothing, result is written in-place
        :rtype: None|Exception
        
        """
        try:
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
                        # Save found printers that can print the selected material
                        printersThatSupportThisMaterial = pgKG.Basics.getSpecificNeighborsByType(entry[NodeDescription.nodeID], NodeTypesAM.printer)
                        if entry[NodeDescription.createdBy] in self.printerDict:
                            self.printerDict[entry[NodeDescription.createdBy]].extend(printersThatSupportThisMaterial)
                        else:
                            self.printerDict[entry[NodeDescription.createdBy]] = printersThatSupportThisMaterial
                        
                
                listOfSetsForManufacturers.append(setOfManufacturerIDs)
            
            if len(listOfSetsForManufacturers) > 0:
                manufacturersWhoCanDoItAll = listOfSetsForManufacturers[0].intersection(*listOfSetsForManufacturers[1:])

                if len(manufacturersWhoCanDoItAll) > 0:
                    if len(self.resultDict) > 0:
                        copiedDict = copy.deepcopy(self.resultDict)
                        for alreadyFilteredManufacturer in self.resultDict:
                            if alreadyFilteredManufacturer not in manufacturersWhoCanDoItAll:
                                copiedDict.pop(alreadyFilteredManufacturer)
                        self.resultDict.clear()
                        self.resultDict.update(copiedDict)
                    else:
                        for manufacturer in manufacturersWhoCanDoItAll:
                            self.resultDict[manufacturer] = manufacturer
        except Exception as e:
            loggerError.error(f"Error in filterByMaterial: {e}")
            return e
        

    ##################################################
    def filterByPostProcessings(self, chosenPostProcessings:dict) -> None|Exception:
        """
        Filter by post-processings choice, must be called after filterByMaterial

        :param resultDict: Where the found manufacturers go
        :type resultDict: dict
        :param chosenPostProcessings: The post-processings in the serviceDetails
        :type chosenPostProcessings: dict
        :return: Nothing, result is written in-place
        :rtype: None|Exception
        
        """
        try:
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
                    if len(self.resultDict) > 0:
                        copiedDict = copy.deepcopy(self.resultDict)
                        for alreadyFilteredManufacturer in self.resultDict:
                            # filter out those, who don't support all selected post-processings
                            if alreadyFilteredManufacturer not in manufacturersWhoCanDoItAll:
                                copiedDict.pop(alreadyFilteredManufacturer)
                                # also remove contractors and their printers
                                if alreadyFilteredManufacturer in self.printerDict:
                                    self.printerDict.pop(alreadyFilteredManufacturer)
                        self.resultDict.clear()
                        self.resultDict.update(copiedDict)
                    else:
                        for manufacturer in manufacturersWhoCanDoItAll:
                            self.resultDict[manufacturer] = manufacturer
        except Exception as e:
            loggerError.error(f"Error in filterByPostProcessings: {e}")
            return e    

    ##################################################
    def filterByPrinter(self, calculations:dict) -> None|Exception:
        """
        Filter by checking properties of the available printers, must be called after filterByPostProcessings

        :param resultDict: Where the found manufacturers go
        :type resultDict: dict
        :param calculations: The calculations in the serviceDetails
        :type calculations: dict
        :return: Nothing, result is written in-place
        :rtype: None|Exception
        
        """
        try:
            # Contractor must be able to print all files!
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
                    setOfManufacturerIDs = pgKG.LogicAM.getManufacturersWithViablePrinters([calculatedValuesForFile[Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._1],calculatedValuesForFile[Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._2],calculatedValuesForFile[Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._3]], self.printerDict)
                    listOfSetsForManufacturers.append(setOfManufacturerIDs)
            
            if len(listOfSetsForManufacturers) > 0:
                manufacturersWhoCanDoItAll = listOfSetsForManufacturers[0].intersection(*listOfSetsForManufacturers[1:])

                if len(manufacturersWhoCanDoItAll) > 0:
                    copiedDict = copy.deepcopy(self.resultDict)
                    for alreadyFilteredManufacturer in self.resultDict:
                        if alreadyFilteredManufacturer not in manufacturersWhoCanDoItAll:
                            copiedDict.pop(alreadyFilteredManufacturer)
                            # no need to throw out manufacturers from printerDict, as they are already filtered above
                    self.resultDict.clear()
                    self.resultDict.update(copiedDict)
        except Exception as e:
            loggerError.error(f"Error in filterByPrinter: {e}")
            return e

    ##################################################
    def getFilteredContractors(self, chosenMaterials:dict, chosenPostProcessings:dict, calculations:dict) -> list:
        """
        Get the filtered contractors

        :return: List of suitable contractors
        :rtype: list
        
        """
        try:
            retVal = self.filterByMaterial(chosenMaterials)
            if isinstance(retVal, Exception):
                raise retVal
            retVal = self.filterByPostProcessings(chosenPostProcessings)
            if isinstance(retVal, Exception):
                raise retVal
            retVal = self.filterByPrinter(calculations)
            if isinstance(retVal, Exception):
                raise retVal
            return self.resultDict.values()
        except Exception as e:
            loggerError.error(f"Error in getFilteredContractors: {e}")
            raise e
        
    ##################################################
    def getPrintersOfAContractor(self, contractorID:str) -> list:
        """
        Get the printers of a contractor

        :param contractorID: The contractor in question
        :type contractorID: str
        :return: List of printers
        :rtype: list
        
        """
        try:
            return self.printerDict[contractorID]
        except Exception as e:
            loggerError.error(f"Error in getPrinters: {e}")
            return []