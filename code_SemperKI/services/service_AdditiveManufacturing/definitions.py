"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""

import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

##################################################
# What makes up the 3D print service
class ServiceDetails(StrEnumExactlyAsDefined):
    """
    What does the service consists of 

    """
    models = enum.auto()
    materials = enum.auto()
    postProcessings = enum.auto()
    calculations = enum.auto()

##################################################
# What defines a material?
class MaterialDetails(StrEnumExactlyAsDefined):
    """
    What does a material entry contain?
    """
    id = enum.auto()
    title = enum.auto()
    propList = enum.auto()
    imgPath = enum.auto()


##################################################
# What defines a material?
class PostProcessDetails(StrEnumExactlyAsDefined):
    """
    What does a postprocess entry contain?
    """
    id = enum.auto()
    title = enum.auto()
    checked = enum.auto()
    selectedValue = enum.auto()
    valueList = enum.auto()
    type = enum.auto()
    imgPath = enum.auto()

##################################################
class NodeTypesAM(StrEnumExactlyAsDefined):
    """
    What possible types can a node have in the AM service?
    
    """
    organization = enum.auto() # the orga node
    printer = enum.auto() # a 3d printer
    material = enum.auto() # a 3d printing material
    additionalRequirement = enum.auto() # what can be done after the print?
    color = enum.auto() # what color should the material have?
    materialCategory = enum.auto() # is the material plastics, metal, ...?
    technology = enum.auto() # Powder Bed, Extrusion, ...
    materialType = enum.auto() # What type is the material, e.g. PLA, ABS, ...?

##################################################
class NodePropertiesAM(StrEnumExactlyAsDefined):
    """
    What are the properties, a node can have?

    """
    imgPath = enum.auto()  # mocks.testPicture  -> printer|material|additionalRequirement|color
    foodSafe = enum.auto()  #"FDA;10/2011" -> material|color
    heatResistant = enum.auto()  #250 -> material|color|additionalRequirement
    flexible = enum.auto()  # 0.5Z50;0.7Z100;4.8XY50;3.7XY100 -> material
    smooth = enum.auto()  # 20Ra -> material|additionalRequirement
    eModul = enum.auto()  # 1358Z;2030XY -> material
    poissonRatio = enum.auto()  #0.35 -> material
    color = enum.auto()  # 9005RAL;Black -> color
    buildVolume = enum.auto()  # 100x100x100 -> printer
    nozzleDiameter = enum.auto() # 0.4 mm -> printer
    certificates = enum.auto() # CE, MD, ... -> printer, material, ...

# TODO: Service Status Codes