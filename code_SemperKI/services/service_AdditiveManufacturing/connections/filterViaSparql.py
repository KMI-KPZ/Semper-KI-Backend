"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions using the sparql queries to filter for contractors
"""

import copy, logging
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertyDescription
from code_SemperKI.modelFiles.processModel import Process, ProcessInterface

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
        self.resultGroups = []
        self.printerGroups = []

    ##################################################
    def filterByMaterial(self, chosenMaterial:dict, groupIdx:int) -> None|Exception:
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

            setOfManufacturerIDs = set()
            material = pgKnowledgeGraph.Basics.getNode(chosenMaterial[MaterialDetails.id])
            nodesWithTheSameUID = pgKnowledgeGraph.Basics.getAllNodesThatShareTheUniqueID(material.uniqueID)
            # filter for those of orgas and retrieve the orgaID
            for entry in nodesWithTheSameUID:
                if entry[NodeDescription.createdBy] != pgKnowledgeGraph.defaultOwner:
                    setOfManufacturerIDs.add(entry[NodeDescription.createdBy])
                    # Save found printers that can print the selected material
                    printersThatSupportThisMaterial = pgKG.Basics.getSpecificNeighborsByType(entry[NodeDescription.nodeID], NodeTypesAM.printer)
                    if entry[NodeDescription.createdBy] in self.printerGroups[groupIdx]:
                        self.printerGroups[groupIdx][entry[NodeDescription.createdBy]].extend(printersThatSupportThisMaterial)
                    else:
                        self.printerGroups[groupIdx][entry[NodeDescription.createdBy]] = printersThatSupportThisMaterial
                        
                
            listOfSetsForManufacturers.append(setOfManufacturerIDs)
            
            if len(listOfSetsForManufacturers) > 0:
                manufacturersWhoCanDoItAll = listOfSetsForManufacturers[0].intersection(*listOfSetsForManufacturers[1:])

                if len(manufacturersWhoCanDoItAll) > 0:
                    if len(self.resultGroups[groupIdx]) > 0:
                        copiedDict = copy.deepcopy(self.resultGroups[groupIdx])
                        for alreadyFilteredManufacturer in self.resultGroups[groupIdx]:
                            if alreadyFilteredManufacturer not in manufacturersWhoCanDoItAll:
                                copiedDict.pop(alreadyFilteredManufacturer)
                        self.resultGroups[groupIdx].clear()
                        self.resultGroups[groupIdx].update(copiedDict)
                    else:
                        for manufacturer in manufacturersWhoCanDoItAll:
                            self.resultGroups[groupIdx][manufacturer] = manufacturer
            elif len(chosenMaterial) > 0:
                self.resultGroups[groupIdx].clear()
        except Exception as e:
            loggerError.error(f"Error in filterByMaterial: {e}")
            return e
        

    ##################################################
    def filterByPostProcessings(self, chosenPostProcessings:dict, groupIdx:int) -> None|Exception:
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
                    if len(self.resultGroups[groupIdx]) > 0:
                        copiedDict = copy.deepcopy(self.resultGroups[groupIdx])
                        for alreadyFilteredManufacturer in self.resultGroups[groupIdx]:
                            # filter out those, who don't support all selected post-processings
                            if alreadyFilteredManufacturer not in manufacturersWhoCanDoItAll:
                                copiedDict.pop(alreadyFilteredManufacturer)
                                # also remove contractors and their printers
                                if alreadyFilteredManufacturer in self.printerGroups[groupIdx]:
                                    self.printerGroups[groupIdx].pop(alreadyFilteredManufacturer)
                        self.resultGroups[groupIdx].clear()
                        self.resultGroups[groupIdx].update(copiedDict)
                    else:
                        for manufacturer in manufacturersWhoCanDoItAll:
                            self.resultGroups[groupIdx][manufacturer] = manufacturer
            elif len(chosenPostProcessings) > 0:
                self.resultGroups[groupIdx].clear()
        except Exception as e:
            loggerError.error(f"Error in filterByPostProcessings: {e}")
            return e    

    ##################################################
    def filterByPrinter(self, calculations:dict, groupIdx:int) -> None|Exception:
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
                    setOfManufacturerIDs = pgKG.LogicAM.getManufacturersWithViablePrinters([calculatedValuesForFile[Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._1],calculatedValuesForFile[Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._2],calculatedValuesForFile[Calculations.measurements][Measurements.mbbDimensions][MbbDimensions._3]], self.printerGroups[groupIdx])
                    if len(setOfManufacturerIDs) > 0:
                        listOfSetsForManufacturers.append(setOfManufacturerIDs)
            
            if len(listOfSetsForManufacturers) > 0:
                manufacturersWhoCanDoItAll = listOfSetsForManufacturers[0].intersection(*listOfSetsForManufacturers[1:])

                if len(manufacturersWhoCanDoItAll) > 0:
                    copiedDict = copy.deepcopy(self.resultGroups[groupIdx])
                    for alreadyFilteredManufacturer in self.resultGroups[groupIdx]:
                        if alreadyFilteredManufacturer not in manufacturersWhoCanDoItAll:
                            copiedDict.pop(alreadyFilteredManufacturer)
                            # no need to throw out manufacturers from printerDict, as they are already filtered above
                    self.resultGroups[groupIdx].clear()
                    self.resultGroups[groupIdx].update(copiedDict)
            elif len(calculations) > 0:
                self.resultGroups[groupIdx].clear()
        except Exception as e:
            loggerError.error(f"Error in filterByPrinter: {e}")
            return e

    ##################################################
    def getFilteredContractors(self, processObj:ProcessInterface|Process) -> list:
        """
        Get the filtered contractors

        :return: List of suitable contractors
        :rtype: list
        
        """
        try:
            self.resultGroups = [{} for i in range(len(processObj.serviceDetails[ServiceDetails.groups]))]
            self.printerGroups = [{} for i in range(len(processObj.serviceDetails[ServiceDetails.groups]))]
            for groupIdx, group in enumerate(processObj.serviceDetails[ServiceDetails.groups]):
                retVal = self.filterByMaterial(processObj.serviceDetails[ServiceDetails.groups][groupIdx][ServiceDetails.material], groupIdx)
                if isinstance(retVal, Exception):
                    raise retVal
                chosenPostProcessings = processObj.serviceDetails[ServiceDetails.groups][groupIdx][ServiceDetails.postProcessings]
                if chosenPostProcessings != {}:
                    retVal = self.filterByPostProcessings(chosenPostProcessings, groupIdx)
                    if isinstance(retVal, Exception):
                        raise retVal
                calculations = processObj.serviceDetails[ServiceDetails.groups][groupIdx][ServiceDetails.calculations]
                retVal = self.filterByPrinter(calculations, groupIdx)
                if isinstance(retVal, Exception):
                    raise retVal
            # TODO: do something with the information, that is inside every group. For now, just return the whole thing
            outList = []
            for group in self.resultGroups:
                outList.extend(group.values())
            return list(set(outList))
        except Exception as e:
            loggerError.error(f"Error in getFilteredContractors: {e}")
            raise e
        
    ##################################################
    def getPrintersOfAContractor(self, contractorID:str, groupIdx:int) -> list:
        """
        Get the printers of a contractor

        :param contractorID: The contractor in question
        :type contractorID: str
        :return: List of printers
        :rtype: list
        
        """
        try:
            return self.printerGroups[groupIdx][contractorID]
        except Exception as e:
            loggerError.error(f"Error in getPrinters: {e}")
            return []