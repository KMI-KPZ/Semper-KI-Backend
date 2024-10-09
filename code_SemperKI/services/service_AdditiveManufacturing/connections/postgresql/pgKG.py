"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Am specific database knowledge graph stuff 
""" 

#from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import 

from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertiesTypesOfEntries, NodePropertyDescription
from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import Logic, Basics

from ...definitions import NodeTypesAM, NodePropertiesAM

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
            outList.append({NodePropertyDescription.name: NodePropertiesAM.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.buildVolume,
                            NodePropertyDescription.value: "int x int x int",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.nozzleDiameter,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
        case NodeTypesAM.material:
            outList.append({NodePropertyDescription.name: NodePropertiesAM.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.heatResistant,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.flexible,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.smooth,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.eModul,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.poissonRatio,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.number})
        case NodeTypesAM.additionalRequirement:
            outList.append({NodePropertyDescription.name: NodePropertiesAM.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.heatResistant,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.smooth,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
        case NodeTypesAM.color:
            outList.append({NodePropertyDescription.name: NodePropertiesAM.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.foodSafe,
                            NodePropertyDescription.value: "License;License;...",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.string})
            outList.append({NodePropertyDescription.name: NodePropertiesAM.color,
                            NodePropertyDescription.value: "Number RAL;#Hex",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.color})
        case NodeTypesAM.materialType:
            outList.append({NodePropertyDescription.name: NodePropertiesAM.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.materialCategory:
            outList.append({NodePropertyDescription.name: NodePropertiesAM.imgPath,
                            NodePropertyDescription.value: "",
                            NodePropertyDescription.type: NodePropertiesTypesOfEntries.text})
        case NodeTypesAM.technology:
            outList.append({NodePropertyDescription.name: NodePropertiesAM.imgPath,
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
        printers = Basics.getNodesByTypeAndProperty(NodeTypesAM.printer, NodePropertiesAM.buildVolume)
        for printer in printers:
            for property in printer[NodeDescription.properties]:
                if property[NodePropertyDescription.name] == NodePropertiesAM.buildVolume:
                    buildVolumeArray = property[NodePropertyDescription.value].split("x")
                    if calculatedValues[0] <= float(buildVolumeArray[0]) and \
                        calculatedValues[1] <= float(buildVolumeArray[1]) and \
                        calculatedValues[2] <= float(buildVolumeArray[2]):
                            manufacturers = (Basics.getSpecificNeighborsByType(printer[NodeDescription.nodeID], NodeTypesAM.organization))
                            for manufacturer in manufacturers:
                                setOfManufacturerIDs.add(manufacturer[NodeDescription.nodeID])
        return setOfManufacturerIDs