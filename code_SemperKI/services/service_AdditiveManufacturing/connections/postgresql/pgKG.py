"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Am specific database knowledge graph stuff 
""" 

#from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import 

from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertiesTypesOfEntries, NodePropertyDescription
from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import Logic, Basics
from code_SemperKI.utilities.locales import manageTranslations

from ...definitions import *

##################################################
def getPropertyDefinitionForNodeType(nodeType:str, userLocale:str) -> list[dict]:
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
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.imgPath]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.nozzleDiameter]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.nozzleDiameter,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.certificates]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.lossOfMaterial]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.lossOfMaterial,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "%",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.fixedCosts]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.fixedCosts,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.machineBatchDistance]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.machineBatchDistance,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.fillRate]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.fillRate,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "%",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.chamberBuildHeight]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.chamberBuildHeight,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.chamberBuildWidth]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.chamberBuildWidth,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.chamberBuildLength]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.chamberBuildLength,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.buildRate]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.buildRate,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "cm³/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.averagePowerConsumption]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.averagePowerConsumption,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/kWh",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.possibleLayerHeights]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.possibleLayerHeights,
                            NodePropertyDescription.value: "15, 75",
                            NodePropertyDescription.unit: "µm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.machineUsageCosts]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.machineUsageCosts,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.machineSurfaceArea]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.machineSurfaceArea,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "m²",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.simpleMachineSetUp]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.simpleMachineSetUp,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.complexMachineSetUp]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.complexMachineSetUp,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.machineHourlyRate]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.machineHourlyRate,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.costRatePersonalMachine]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.costRatePersonalMachine,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.coatingTime]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.coatingTime,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMPrinter.maxPrintingSpeed]),
                            NodePropertyDescription.key: NodePropertiesAMPrinter.maxPrintingSpeed,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "cm/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
        case NodeTypesAM.material:
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.imgPath]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.foodSafe]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.heatResistant]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.heatResistant,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "°C",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.flexible]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.flexible,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "MPa",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.smooth]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.smooth,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "Ra",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.eModul]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.eModul,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "MPa",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.poissonRatio]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.poissonRatio,
                            NodePropertyDescription.value: "1",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.certificates]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.density]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.density,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "g/cm³",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.printingSpeed]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.printingSpeed,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "cm/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.acquisitionCosts]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.acquisitionCosts,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/kg",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.ultimateTensileStrength]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.ultimateTensileStrength,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "MPa",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.tensileModulus]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.tensileModulus,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "GPa",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.elongationAtBreak]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.elongationAtBreak,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "%",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.flexuralStrength]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.flexuralStrength,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "MPa",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterial.specificMaterialType]),
                            NodePropertyDescription.key: NodePropertiesAMMaterial.specificMaterialType,
                            NodePropertyDescription.value: "PLA, ABS, ...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.additionalRequirement:
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMAdditionalRequirement.imgPath]),
                            NodePropertyDescription.key: NodePropertiesAMAdditionalRequirement.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMAdditionalRequirement.foodSafe]),
                            NodePropertyDescription.key: NodePropertiesAMAdditionalRequirement.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMAdditionalRequirement.heatResistant]),
                            NodePropertyDescription.key: NodePropertiesAMAdditionalRequirement.heatResistant,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "°C",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMAdditionalRequirement.smooth]),
                            NodePropertyDescription.key: NodePropertiesAMAdditionalRequirement.smooth,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "MPa",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMAdditionalRequirement.certificates]),
                            NodePropertyDescription.key: NodePropertiesAMAdditionalRequirement.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMAdditionalRequirement.treatmentCosts]),
                            NodePropertyDescription.key: NodePropertiesAMAdditionalRequirement.treatmentCosts,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMAdditionalRequirement.fixedCosts]),
                            NodePropertyDescription.key: NodePropertiesAMAdditionalRequirement.fixedCosts,
                            NodePropertyDescription.value: "0",
                            NodePropertyDescription.unit: "€",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
        case NodeTypesAM.color:
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMColor.imgPath]),
                            NodePropertyDescription.key: NodePropertiesAMColor.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMColor.colorHEX]),
                            NodePropertyDescription.key: NodePropertiesAMColor.colorHEX,
                            NodePropertyDescription.value: "#000000, #FFFFFF",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.array})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMColor.colorRAL]),
                            NodePropertyDescription.key: NodePropertiesAMColor.colorRAL,
                            NodePropertyDescription.value: "RAL 1000",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMColor.certificates]),
                            NodePropertyDescription.key: NodePropertiesAMColor.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.materialType:
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterialType.imgPath]),
                            NodePropertyDescription.key: NodePropertiesAMMaterialType.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.materialCategory:
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMMaterialCategory.imgPath]),
                            NodePropertyDescription.key: NodePropertiesAMMaterialCategory.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.unit: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.technology:
            outList.append({NodePropertyDescription.name: manageTranslations.getTranslation(userLocale, ["service",SERVICE_NAME,NodePropertiesAMTechnology.imgPath]),
                            NodePropertyDescription.key: NodePropertiesAMTechnology.imgPath,
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
            # filter if printer is active
            if printer[NodeDescription.active] is False:
                continue
            
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

    
