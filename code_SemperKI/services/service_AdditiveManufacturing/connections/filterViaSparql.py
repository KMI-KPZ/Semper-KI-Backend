"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Functions using the sparql queries to filter for contractors
"""

import copy, logging
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph
from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertyDescription
from code_SemperKI.modelFiles.processModel import Process, ProcessInterface
from code_SemperKI.definitions import ContractorParsingForFrontend

from ..connections.postgresql import pgKG, pgVerification
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
        self.errors = []

    ##################################################
    def filterByMaterialAndColor(self, chosenMaterial:dict, chosenColor:dict, groupIdx:int) -> None|Exception:
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

            # they must have all selected materials
            listOfSetsForManufacturers:list[set] = []

            setOfManufacturerIDs = set()
            setOfVerifiedManufacturerIDs = set()
            material = pgKnowledgeGraph.Basics.getNode(chosenMaterial[MaterialDetails.id])
            nodesWithTheSameUID = pgKnowledgeGraph.Basics.getAllNodesThatShareTheUniqueID(material.uniqueID)
            # filter for those of orgas and retrieve the orgaID
            for entry in nodesWithTheSameUID:
                if NodeDescription.active in entry and entry[NodeDescription.active]:
                    if entry[NodeDescription.createdBy] != pgKnowledgeGraph.defaultOwner:
                        addPrinter = False
                        # filter for color
                        if chosenColor != {}:
                            nodesWithTheSameUIDColor = pgKnowledgeGraph.Basics.getAllNodesThatShareTheUniqueID(chosenColor[NodeDescription.uniqueID])
                            for entryColor in nodesWithTheSameUIDColor:
                                if entryColor[NodeDescription.active] and entryColor[NodeDescription.createdBy] == entry[NodeDescription.createdBy] and pgKnowledgeGraph.Basics.getIfEdgeExists(entry[NodeDescription.nodeID], entryColor[NodeDescription.nodeID]):
                                    setOfManufacturerIDs.add(entry[NodeDescription.createdBy])
                                    addPrinter = True
                        else:
                            setOfManufacturerIDs.add(entry[NodeDescription.createdBy])
                            addPrinter = True

                        if addPrinter:
                            # Save found printers that can print the selected material
                            printersThatSupportThisMaterial = pgKG.Basics.getSpecificNeighborsByType(entry[NodeDescription.nodeID], NodeTypesAM.printer)
                            if entry[NodeDescription.createdBy] in self.printerGroups[groupIdx]:
                                self.printerGroups[groupIdx][entry[NodeDescription.createdBy]].extend(printersThatSupportThisMaterial)
                            else:
                                self.printerGroups[groupIdx][entry[NodeDescription.createdBy]] = printersThatSupportThisMaterial
                            
                            # check if the printer and the material are verified for this organization
                            for printer in printersThatSupportThisMaterial:
                                verification = pgVerification.getVerificationObject(entry[NodeDescription.createdBy], printer[NodeDescription.nodeID], chosenMaterial[MaterialDetails.id])
                                if not isinstance(verification, Exception):
                                    if verification.status == pgVerification.VerificationStatus.verified:
                                        setOfVerifiedManufacturerIDs.add(entry[NodeDescription.createdBy])
                                        break
                        else:
                            if chosenColor != {}:
                                self.errors[groupIdx] = {ContractorParsingForFrontend.groupID: groupIdx, ContractorParsingForFrontend.error: FilterErrors.color.value}
        
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
                            if manufacturer in setOfVerifiedManufacturerIDs:
                                self.resultGroups[groupIdx][manufacturer] = (manufacturer, True)
                            else:
                                self.resultGroups[groupIdx][manufacturer] = (manufacturer, False)
            elif len(chosenMaterial) > 0:
                if self.errors[groupIdx] == {}:
                    self.errors[groupIdx] = {ContractorParsingForFrontend.groupID: groupIdx, ContractorParsingForFrontend.error: FilterErrors.material.value}
                # else it is a color error and already set
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
                                    self.printerGroups[groupIdx].pop(alreadyFilteredManufacturer[0])
                        self.resultGroups[groupIdx].clear()
                        self.resultGroups[groupIdx].update(copiedDict)
                    else:
                        for manufacturer in manufacturersWhoCanDoItAll:
                            self.resultGroups[groupIdx][manufacturer] = manufacturer
            elif len(chosenPostProcessings) > 0:
                self.errors[groupIdx] = {ContractorParsingForFrontend.groupID: groupIdx, ContractorParsingForFrontend.error: FilterErrors.postProcessing.value}
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
                self.errors[groupIdx] = {ContractorParsingForFrontend.groupID: groupIdx, ContractorParsingForFrontend.error: FilterErrors.printer.value}
                self.resultGroups[groupIdx].clear()
        except Exception as e:
            loggerError.error(f"Error in filterByPrinter: {e}")
            return e

    ##################################################
    def getFilteredContractors(self, processObj:ProcessInterface|Process) -> dict:
        """
        Get the filtered contractors

        :return: Object with list of suitable contractors
        :rtype: dict
        
        """
        try:
            numberOfGroups = len(processObj.serviceDetails[ServiceDetails.groups])
            self.resultGroups = [{} for i in range(numberOfGroups)]
            self.printerGroups = [{} for i in range(numberOfGroups)]
            self.errors = [{} for i in range(numberOfGroups)]
            for groupIdx, group in enumerate(processObj.serviceDetails[ServiceDetails.groups]):
                retVal = self.filterByMaterialAndColor(processObj.serviceDetails[ServiceDetails.groups][groupIdx][ServiceDetails.material], processObj.serviceDetails[ServiceDetails.groups][groupIdx][ServiceDetails.color], groupIdx)
                if isinstance(retVal, Exception):
                    raise retVal
                if self.errors[groupIdx] != {}: # if there is an error, no need to check post-processings
                    continue
                chosenPostProcessings = processObj.serviceDetails[ServiceDetails.groups][groupIdx][ServiceDetails.postProcessings]
                if chosenPostProcessings != {}:
                    retVal = self.filterByPostProcessings(chosenPostProcessings, groupIdx)
                    if isinstance(retVal, Exception):
                        raise retVal
                    if self.errors[groupIdx] != {}: # if there is an error, no need to check printers
                        continue
                calculations = processObj.serviceDetails[ServiceDetails.groups][groupIdx][ServiceDetails.calculations]
                retVal = self.filterByPrinter(calculations, groupIdx)
                if isinstance(retVal, Exception):
                    raise retVal

            outDict = {}
            for groupIdx, group in enumerate(self.resultGroups):
                for contractorID, contractorTuple in group.items():
                    if contractorID in outDict:
                        if outDict[contractorID][1] is True and contractorTuple[1] is True: # stays verified
                            outDict[contractorID] = (contractorTuple[0], True, outDict[contractorID][2].append(groupIdx))
                        elif outDict[contractorID][1] is True and contractorTuple[1] is False: #not verified anymore
                            outDict[contractorID] = (contractorTuple[0], False, outDict[contractorID][2].append(groupIdx))
                        else:
                            outDict[contractorID][2].append(groupIdx) # was not verified before, stays not verified
                    else:
                        outDict[contractorID] = (contractorTuple[0], contractorTuple[1], [groupIdx])

            return {ContractorParsingForFrontend.contractors: list(outDict.values()), ContractorParsingForFrontend.errors: self.errors}
        except Exception as e:
            loggerError.error(f"Error in getFilteredContractors: {e}")
            return e
        
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