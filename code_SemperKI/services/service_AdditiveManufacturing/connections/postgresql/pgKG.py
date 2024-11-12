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
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.buildVolume,
                            NodePropertyDescription.value: "mm x mm x mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.nozzleDiameter,
                            NodePropertyDescription.value: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.lossOfMaterial,
                            NodePropertyDescription.value: "%",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.fixedCosts,
                            NodePropertyDescription.value: "€",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.machineBatchDistance,
                            NodePropertyDescription.value: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.fillRate,
                            NodePropertyDescription.value: "%",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.chamberBuildHeight,
                            NodePropertyDescription.value: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.chamberBuildWidth,
                            NodePropertyDescription.value: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.chamberBuildLength,
                            NodePropertyDescription.value: "mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.buildRate,
                            NodePropertyDescription.value: "cm³/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.powerCosts,
                            NodePropertyDescription.value: "€/kWh",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.possibleLayerHeights,
                            NodePropertyDescription.value: "0.1 mm, 0.2 mm, 0.3 mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.machineUsageCosts,
                            NodePropertyDescription.value: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.scanSpeed,
                            NodePropertyDescription.value: "mm/s",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.machineSize,
                            NodePropertyDescription.value: "500 mm x 500 mm x 500 mm",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.simpleMachineSetUp,
                            NodePropertyDescription.value: "h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.complexMachineSetUp,
                            NodePropertyDescription.value: "h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMPrinter.machineHourlyRate,
                            NodePropertyDescription.value: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            
        case NodeTypesAM.material:
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.heatResistant,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.flexible,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.smooth,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.eModul,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.poissonRatio,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.supportStructurePartRate,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.density,
                            NodePropertyDescription.value: "g/cm³",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.printingSpeed,
                            NodePropertyDescription.value: "cm³/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterial.acquisitionCosts,
                            NodePropertyDescription.value: "€/kg",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            
        case NodeTypesAM.additionalRequirement:
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.heatResistant,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.smooth,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.treatmentCosts,
                            NodePropertyDescription.value: "€/h",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
            outList.append({NodePropertyDescription.name: NodePropertiesAMAdditionalRequirement.fixedCosts,
                            NodePropertyDescription.value: "€",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})

        case NodeTypesAM.color:
            outList.append({NodePropertyDescription.name: NodePropertiesAMColor.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAMColor.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAMColor.color,
                            NodePropertyDescription.value: "Number RAL;#Hex",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.color})
            outList.append({NodePropertyDescription.name: NodePropertiesAMColor.certificates,
                            NodePropertyDescription.value: "CE, MD, ...",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.materialType:
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterialType.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.materialCategory:
            outList.append({NodePropertyDescription.name: NodePropertiesAMMaterialCategory.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.technology:
            outList.append({NodePropertyDescription.name: NodePropertiesAMTechnology.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})

    return outList

##################################################
class LogicAM(Logic):
    """
    Extending the class for AM usage
    
    """

    ##################################################
    @staticmethod
    def checkBuildVolume(calculatedValues:list[float]) -> set:
        """
        Check if build volume is sufficient
        
        :param calculatedValues: The comparison values
        :type calculatedValues: list[float]
        :return: set of IDs
        :rtype: set

        """
        setOfManufacturerIDs = set()
        printers = Basics.getNodesByTypeAndProperty(NodeTypesAM.printer, NodePropertiesAMPrinter.buildVolume)
        for printer in printers:
            for property in printer[NodeDescription.properties]:
                if property[NodePropertyDescription.name] == NodePropertiesAMPrinter.buildVolume:
                    buildVolumeArray = property[NodePropertyDescription.value].split("x")
                    if calculatedValues[0] <= float(buildVolumeArray[0]) and \
                        calculatedValues[1] <= float(buildVolumeArray[1]) and \
                        calculatedValues[2] <= float(buildVolumeArray[2]):
                            manufacturers = (Basics.getSpecificNeighborsByType(printer[NodeDescription.nodeID], NodeTypesAM.organization))
                            for manufacturer in manufacturers:
                                setOfManufacturerIDs.add(manufacturer[NodeDescription.nodeID])
        return setOfManufacturerIDs