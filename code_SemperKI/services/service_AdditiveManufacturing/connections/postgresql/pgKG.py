"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Am specific database knowledge graph stuff 
""" 

#from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import 

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
            outList.append({"name": NodePropertiesAM.imgPath,
                            "value": "",
                            "type": "text"})
            outList.append({"name": NodePropertiesAM.buildVolume,
                            "value": "int x int x int",
                            "type": "string"})
            outList.append({"name": NodePropertiesAM.nozzleDiameter,
                            "value": "",
                            "type": "number"})
        case NodeTypesAM.material:
            outList.append({"name": NodePropertiesAM.imgPath,
                            "value": "",
                            "type": "text"})
            outList.append({"name": NodePropertiesAM.foodSafe,
                            "value": "License;License;...",
                            "type": "string"})
            outList.append({"name": NodePropertiesAM.heatResistant,
                            "value": "",
                            "type": "string"})
            outList.append({"name": NodePropertiesAM.flexible,
                            "value": "",
                            "type": "string"})
            outList.append({"name": NodePropertiesAM.smooth,
                            "value": "",
                            "type": "string"})
            outList.append({"name": NodePropertiesAM.eModul,
                            "value": "",
                            "type": "string"})
            outList.append({"name": NodePropertiesAM.poissonRatio,
                            "value": "",
                            "type": "number"})
        case NodeTypesAM.additionalRequirement:
            outList.append({"name": NodePropertiesAM.imgPath,
                            "value": "",
                            "type": "text"})
            outList.append({"name": NodePropertiesAM.foodSafe,
                            "value": "License;License;...",
                            "type": "string"})
            outList.append({"name": NodePropertiesAM.heatResistant,
                            "value": "",
                            "type": "string"})
            outList.append({"name": NodePropertiesAM.smooth,
                            "value": "",
                            "type": "string"})
        case NodeTypesAM.color:
            outList.append({"name": NodePropertiesAM.imgPath,
                            "value": "",
                            "type": "text"})
            outList.append({"name": NodePropertiesAM.foodSafe,
                            "value": "License;License;...",
                            "type": "string"})
            outList.append({"name": NodePropertiesAM.color,
                            "value": "Number RAL;#Hex",
                            "type": "color"})
        case NodeTypesAM.materialType:
            outList.append({"name": NodePropertiesAM.imgPath,
                            "value": "",
                            "type": "text"})
        case NodeTypesAM.materialCategory:
            outList.append({"name": NodePropertiesAM.imgPath,
                            "value": "",
                            "type": "text"})
        case NodeTypesAM.technology:
            outList.append({"name": NodePropertiesAM.imgPath,
                            "value": "",
                            "type": "text"})

    return outList