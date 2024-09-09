"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Am specific database knowledge graph stuff 
""" 

#from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import 

from ...definitions import NodePropertiesAMObjectDefinition, NodePropertiesAMTypesOfEntries, NodeTypesAM, NodePropertiesAM

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
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.imgPath,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.text})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.buildVolume,
                            NodePropertiesAMObjectDefinition.value: "int x int x int",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.string})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.nozzleDiameter,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.number})
        case NodeTypesAM.material:
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.imgPath,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.text})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.foodSafe,
                            NodePropertiesAMObjectDefinition.value: "License;License;...",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.string})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.heatResistant,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.string})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.flexible,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.string})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.smooth,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.string})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.eModul,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.string})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.poissonRatio,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.number})
        case NodeTypesAM.additionalRequirement:
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.imgPath,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.text})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.foodSafe,
                            NodePropertiesAMObjectDefinition.value: "License;License;...",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.string})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.heatResistant,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.string})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.smooth,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.string})
        case NodeTypesAM.color:
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.imgPath,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.text})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.foodSafe,
                            NodePropertiesAMObjectDefinition.value: "License;License;...",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.string})
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.color,
                            NodePropertiesAMObjectDefinition.value: "Number RAL;#Hex",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.color})
        case NodeTypesAM.materialType:
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.imgPath,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.text})
        case NodeTypesAM.materialCategory:
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.imgPath,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.text})
        case NodeTypesAM.technology:
            outList.append({NodePropertiesAMObjectDefinition.name: NodePropertiesAM.imgPath,
                            NodePropertiesAMObjectDefinition.value: "",
                            NodePropertiesAMObjectDefinition.type: NodePropertiesAMTypesOfEntries.text})

    return outList