"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Am specific database knowledge graph stuff 
""" 

#from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import 

from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertiesTypesOfEntries, NodePropertyDescription
from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import Logic, Basics

from ...definitions import *

##################################################
def getPropertyDefinitionForNodeType(nodeType:str) -> list[dict]:
    """
    For different node types, different properties are important. 
    Retrieve those, especially for the Frontend.

    :param nodeType: The type of the node
    :type nodeType: str
    :return: A list of the properties, defined properly
    :rtype: list[dict] / JSON
    
    """
    outList = []
    match nodeType:
        case NodeTypesAM.organization:
            pass
        case NodeTypesAM.printer:
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.nozzleDiameter,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.lossOfMaterial,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "%",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.fixedCosts,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.machineBatchDistance,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.fillRate,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "%",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.chamberBuildHeight,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.chamberBuildWidth,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.chamberBuildLength,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.buildRate,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "cm³/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.averagePowerConsumption,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/kWh",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.possibleLayerHeights,
                            NodePropertyDescription.value: "15, 75",
                            NodePropertyDescription.unit: "µm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.machineUsageCosts,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            #outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.scanSpeed,
            #                NodePropertyDescription.value: "mm/s",
            #                NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.machineSurfaceArea,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "m²",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.simpleMachineSetUp,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.complexMachineSetUp,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.machineHourlyRate,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.costRatePersonalMachine,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.coatingTime,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.maxPrintingSpeed,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "cm/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            
        case NodeTypesAM.material:
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.heatResistant,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "°C",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.flexible,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "MPa",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.smooth,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "Ra",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.eModul,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "MPa",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.poissonRatio,
                            NodePropertyDescription.value: "1",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.density,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "g/cm³",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.printingSpeed,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "cm/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.acquisitionCosts,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/kg",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            
        case NodeTypesAM.additionalRequirement:
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.heatResistant,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "°C",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.smooth,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "MPa",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.treatmentCosts,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.fixedCosts,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})

        case NodeTypesAM.color:
            outList.append({NodePropertyDescription.name: NodePropertiesAMColor.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMColor.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMColor.color,
                            NodePropertyDescription.value: "000000",
                            NodePropertyDescription.unit: "#Hex",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.color})
            outList.append({NodePropertyDescription.name: NodePropertiesAMColor.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.materialType:
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterialType.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.materialCategory:
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterialCategory.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.technology:
            outList.append({NodePropertyDescription.name: NodePropertiesAMTechnology.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})

    return outList

##################################################
class LogicAM(Logic):
    """
    Extending the class for AM usage
    
    """

    ##################################################
    @staticmethod
    def getViablePrinters(calculatedValues:dict, listOfPrinters:list) -> list[dict]:
        """
        Get a list of printers that are viable
        
        :param calculatedValues: The comparison values
        :type calculatedValues: dict
        :param prefilteredDictOfNodes: A dictionary containing manufacturers and their printers to be filtered further
        :type prefilteredDictOfNodes: dict with manufacturerID as key and printer lists as values
        :return: List of printer nodes
        :rtype: list[dict]

        """
        listOfViablePrinters = []
        # filter by material, post-processings, build plate, etc...

        for printer in listOfPrinters:
            chamberHeight = 0
            chamberWidth = 0
            chamberLength = 0
            for printerProperty in printer[NodeDescription.properties]:
                # filter via build volume
                if printerProperty[NodePropertyDescription.name] == NodePropertiesAMPrinter.chamberBuildHeight:
                    chamberHeight = float(printerProperty[NodePropertyDescription.value])
                elif printerProperty[NodePropertyDescription.name] == NodePropertiesAMPrinter.chamberBuildWidth:
                    chamberWidth = float(printerProperty[NodePropertyDescription.value])
                elif printerProperty[NodePropertyDescription.name] == NodePropertiesAMPrinter.chamberBuildLength:
                    chamberLength = float(printerProperty[NodePropertyDescription.value])

            if (calculatedValues[0] <= float(chamberLength) and \
                calculatedValues[1] <= float(chamberWidth)) or \
                (calculatedValues[0] <= float(chamberWidth) and \
                 calculatedValues[1] <= float(chamberLength)) and \
                calculatedValues[2] <= float(chamberHeight):
                listOfViablePrinters.append(printer)
                break
                       
        return listOfViablePrinters

    ##################################################
    @staticmethod
    def getManufacturersWithViablePrinters(calculatedValues:list[float], prefilteredDictOfNodes:dict) -> set:
        """
        Check if there are manufacturers who have printers that are sufficient
        
        :param calculatedValues: The comparison values
        :type calculatedValues: list[float]
        :param prefilteredDictOfNodes: A dictionary containing manufacturers and their printers to be filtered further
        :type prefilteredDictOfNodes: dict with manufacturerID as key and printer lists as values
        :return: set of IDs
        :rtype: set

        """
        setOfManufacturerIDs = set()
        throwOuts = []
        for manufacturerID in prefilteredDictOfNodes:
            prefilteredDictOfNodes[manufacturerID] = LogicAM.getViablePrinters(calculatedValues, prefilteredDictOfNodes[manufacturerID])
            if len(prefilteredDictOfNodes[manufacturerID]) > 0:
                setOfManufacturerIDs.add(manufacturerID)
            else:
                # remove manufacturer from printerDict
                throwOuts.append(manufacturerID)
        for manufacturerID in throwOuts:
            if len(prefilteredDictOfNodes[manufacturerID]) == 0:
                prefilteredDictOfNodes.pop(manufacturerID)

        return setOfManufacturerIDs

    
