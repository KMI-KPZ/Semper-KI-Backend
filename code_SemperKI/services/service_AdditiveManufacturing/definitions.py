"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""

import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

##################################################
# Service specific definitions
SERVICE_NAME = "ADDITIVE_MANUFACTURING"
SERVICE_NUMBER = 1

##################################################
# What makes up the 3D print service
class ServiceDetails(StrEnumExactlyAsDefined):
    """
    What does the service consists of 

    """
    groups = enum.auto()
    models = enum.auto()
    material = enum.auto()
    postProcessings = enum.auto()
    calculations = enum.auto()
    color = enum.auto()
    context = enum.auto()

##################################################
# Additional FileContents
class FileContentsAM(StrEnumExactlyAsDefined):
    """
    What does a file contain?

    """
    width = enum.auto() # int
    height = enum.auto() # int
    length = enum.auto() # int
    volume = enum.auto() # int
    complexity = enum.auto() # int
    scalingFactor = enum.auto()
    femRequested = enum.auto() # bool
    testType = enum.auto() # str, elongation or compression
    pressure = enum.auto() # int in MPa

##################################################
# How do the calculations look like?
class Calculations(StrEnumExactlyAsDefined):
    """
    What does a calculation entry contain?
    """
    filename = enum.auto()
    measurements = enum.auto()
    status_code = enum.auto()

##################################################
# How do measurements look like?
class Measurements(StrEnumExactlyAsDefined):
    """
    What does a measurement entry contain?
    """
    volume = enum.auto()
    surfaceArea = enum.auto()
    mbbDimensions = enum.auto()
    mbbVolume = enum.auto()

##################################################
# How do mbbDimensions look like?
class MbbDimensions(StrEnumExactlyAsDefined):
    """
    What does a mbbDimensions entry contain?
    """
    _1 = enum.auto()
    _2 = enum.auto()
    _3 = enum.auto()

##################################################
# What defines a material?
class MaterialDetails(StrEnumExactlyAsDefined):
    """
    What does a material entry contain?
    """
    id = enum.auto()
    title = enum.auto()
    imgPath = enum.auto()
    medianPrice = enum.auto()
    propList = enum.auto()
    colors = enum.auto()

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
class NodePropertiesAMPrinter(StrEnumExactlyAsDefined):
    """
    What are the properties, a printer node can have?

    """
    imgPath = enum.auto()  # mocks.testPicture
    nozzleDiameter = enum.auto() # 0.4 mm
    certificates = enum.auto() # CE, MD, ...
    lossOfMaterial = enum.auto() # 0.1%
    fixedCosts = enum.auto() # 1000
    machineBatchDistance = enum.auto() # 0.1 mm
    fillRate = enum.auto() # 0.5
    chamberBuildHeight = enum.auto() # 100 mm
    chamberBuildWidth = enum.auto() # 100 mm
    chamberBuildLength = enum.auto() # 100 mm
    buildRate = enum.auto() # cm³/h
    averagePowerConsumption = enum.auto() # €/kWh
    possibleLayerHeights = enum.auto() # [0.1, 0.2, 0.3, 0.4, 0.5]
    machineUsageCosts = enum.auto() # €/h
    #scanSpeed = enum.auto() # mm/s
    machineSurfaceArea = enum.auto() # 100 m²
    simpleMachineSetUp = enum.auto() # 0.1 h
    complexMachineSetUp = enum.auto() # 0.5 h
    machineHourlyRate = enum.auto() # €/h
    costRatePersonalMachine = enum.auto() # €/h
    coatingTime = enum.auto() # 0.1 h
    maxPrintingSpeed = enum.auto() # 100 cm/h

##################################################
class NodePropertiesAMMaterial(StrEnumExactlyAsDefined):
    """
    What are the properties, a material node can have?
    """
    imgPath = enum.auto() # mocks.testPicture
    foodSafe = enum.auto() #"FDA;10/2011"
    heatResistant = enum.auto() #250
    flexible = enum.auto()  # 0.5Z50;0.7Z100;4.8XY50;3.7XY100
    smooth = enum.auto()  # 20Ra
    eModul = enum.auto()  # 1358Z;2030XY
    poissonRatio = enum.auto()  #0.35
    certificates = enum.auto() # CE, MD, ...
    density = enum.auto() # 1.2 g/cm³
    printingSpeed = enum.auto() # 100 cm/h
    acquisitionCosts = enum.auto() # €/kg
    ultimateTensileStrength = enum.auto() # MPa
    tensileModulus = enum.auto() # GPa
    elongationAtBreak = enum.auto() # %
    flexuralStrength = enum.auto() # MPa
    specificMaterialType = enum.auto() # PLA, ABS, ...

##################################################
class NodePropertiesAMAdditionalRequirement(StrEnumExactlyAsDefined):
    """
    What are the properties, a additional requirement node can have?
    """
    imgPath = enum.auto() # mocks.testPicture
    heatResistant = enum.auto()  #250
    smooth = enum.auto()  # 20Ra
    foodSafe = enum.auto() #"FDA;10/2011"
    certificates = enum.auto() # CE, MD, ...
    treatmentCosts = enum.auto() # €/h
    fixedCosts = enum.auto() # €

##################################################
class NodePropertiesAMColor(StrEnumExactlyAsDefined):
    """
    What are the properties, a color node can have?
    """
    imgPath = enum.auto() # mocks.testPicture
    colorRAL = enum.auto()  # RAL 9005
    colorHEX = enum.auto()  # #000000;#FFFFFF
    certificates = enum.auto() # CE, MD, ...

##################################################
class NodePropertiesAMMaterialCategory(StrEnumExactlyAsDefined):
    """
    What are the properties, a material category node can have?
    """
    imgPath = enum.auto()  # mocks.testPicture

##################################################
class NodePropertiesAMTechnology(StrEnumExactlyAsDefined):
    """
    What are the properties, a technology node can have?
    """
    imgPath = enum.auto()  # mocks.testPicture

##################################################
class NodePropertiesAMMaterialType(StrEnumExactlyAsDefined):
    """
    What are the properties, a material type node can have?
    """
    imgPath = enum.auto()  # mocks.testPicture


##################################################
class OrganizationDetailsAM(StrEnumExactlyAsDefined):
    """
    What are the details of an organization?
    
    """
    powerCosts = enum.auto()
    margin = enum.auto()
    personnelCosts = enum.auto()
    costRatePersonnelEngineering = enum.auto()
    repairCosts = enum.auto()
    additionalFixedCosts = enum.auto()
    costRateEquipmentEngineering = enum.auto()
    fixedCostsEquipmentEngineering = enum.auto()
    safetyGasCosts = enum.auto()
    roomCosts = enum.auto()

# TODO: Service Status Codes

##################################################
class ServiceSpecificDetailsForContractors(StrEnumExactlyAsDefined):
    """
    What are the details of a service for contractors?
        
    """
    verified = enum.auto()
    groups = enum.auto()

##################################################
class FilterCategories(StrEnumExactlyAsDefined):
    """
    What filters can be applied?

    """
    materialCategory = enum.auto()
    materialType = enum.auto()
    tensileStrength = enum.auto()
    density = enum.auto()
    elongationAtBreak = enum.auto()
    certificates = enum.auto()


##################################################
class FilterErrors(StrEnumExactlyAsDefined):
    """
    What can go wrong when filtering?
    
    """
    material = enum.auto()
    color = enum.auto()
    postProcessing = enum.auto()
    printer = enum.auto()