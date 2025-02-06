#models.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal



# Enumeration of 3D printer types
class PrinterType(str, Enum):
    """
    Enumeration for the different types of 3D printing technologies.
    """
    binder_jetting = "Binder Jetting"
    directed_energy_deposition = "Directed Energy Deposition"
    material_extrusion = "Material Extrusion"
    material_jetting = "Material Jetting"
    powder_bed_fusion = "Powder Bed Fusion"
    sheet_lamination = "Sheet Lamination"
    vat_photopolymerization = "Vat Photopolymerization"
    not_reported = "Not reported"


# Enumeration of organization types
class OrganizationType(str, Enum):
    """
    Enumeration for the type of organization associated with the printer.
    It could be a manufacturer, distributor, service provider, etc.
    """
    manufacturer = "manufacturer"
    distributor = "distributor"
    service_provider = "service_provider"
    research_institution = "research_institution"
    other = "other"


# Model representing an organization
class Organization(BaseModel):
    """
    Represents an organization involved with the 3D printer.
    This could be a manufacturer, distributor, or service provider.
    """
    type: OrganizationType
    organization_name: str


# Model for dimensions and physical properties
class Dimension(BaseModel):
    """
    Represents a dimension with a value and a unit.
    Used for defining dimensions like width, length, or height.
    """
    value: float
    unit: str



class PrinterDimensions(BaseModel):
    """
    Represents the physical dimensions of the printer.
    This includes width, length, and height dimensions.
    """
    width: Dimension
    length: Dimension
    height: Dimension


class MachineSurfaceArea(BaseModel):
    """
    Represents the surface area of the machine with a unit (e.g., m², ft²).
    """
    value: float  # The surface area value
    unit: str  # Unit of surface area, e.g., m², ft²

    def __init__(self, **data):
        data['unit'] = data.get('unit', "m²")  # Set default unit to m² if not provided
        super().__init__(**data)


class PhysicalProperties(BaseModel):
    """
    Represents the weight of the printer along with its dimensions.
    """
    weight: Dimension  # The weight of the printer
    dimensions: PrinterDimensions  # The physical dimensions of the printer
    #machine_surface_area: Optional[MachineSurfaceArea]

# Build volume and layer thickness models
class BuildVolume(BaseModel):
    width: Dimension
    length: Dimension
    height: Dimension


class LayerThickness(BaseModel):
    """
    Represents the layer thickness specifications for 3D printing.
    """
    min_thickness: Dimension  # Minimum layer thickness
    max_thickness: Dimension  # Maximum layer thickness


# New features: Chamber build dimensions, batch distance, and build rate
class ChamberBuild(BaseModel):
    """
    Represents the dimensions of the build chamber and batch settings.
    """
    width: Dimension  # Width of the build chamber
    length: Dimension  # Length of the build chamber
    height: Dimension  # Height of the build chamber

class PrintingSpeed(BaseModel):
    """
    Represents the physical properties of the material.
    """
    printing_speed: Dimension


class BuildRate(BaseModel):
    """
    Represents the build rate of the printer.
    """
    value: float  # The build rate value
    unit: str  # Unit of build rate, e.g., cm³/h

    def __init__(self, **data):
        data['unit'] = data.get('unit', "cm³/h")  # Set default if not provided
        super().__init__(**data)


# Model for representing power consumption
class PowerConsumption(BaseModel):
    """
    Represents the average power consumption of the printer.
    """
    value: float  # Average power consumption value
    unit: str  # Unit for power consumption, defaulting to €/kWh

    def __init__(self, **data):
        data['unit'] = data.get('unit', "€/kWh")  # Default to €/kWh if not provided
        super().__init__(**data)


# Enumeration for various certifications
class Certification(str, Enum):
    """
    Enumeration for different certifications that a 3D printer might have.
    """
    CE = "CE"
    FDA = "FDA"
    EMC = "EMC"
    ISO = "ISO"
    UL = "UL"
    RoHS = "RoHS"
    other = "Other"



# Enumeration for various file formats
class FileFormat(str, Enum):
    """
    Enumeration for common input file formats supported by 3D printers.
    """
    STL = "STL"  # Stereolithography
    OBJ = "OBJ"  # Wavefront Object
    AMF = "AMF"  # Additive Manufacturing File Format
    _3MF = "3MF"  # 3D Manufacturing Format
    PLY = "PLY"  # Polygon File Format
    GCODE = "GCODE"  # G-code, widely used for 3D printing
    STEP = "STEP"  # Standard for the Exchange of Product Model Data
    IGES = "IGES"  # Initial Graphics Exchange Specification
    X3D = "X3D"  # Extensible 3D
    VRML = "VRML"  # Virtual Reality Modeling Language
    other = "Other"  # For custom or unsupported formats


# Printer specifications model
class PrinterSpecifications(BaseModel):
    """
    Core specifications of the printer.
    """
    printing_technology: PrinterType
    build_volume: BuildVolume
    layer_thickness: LayerThickness
    possible_layer_heights: Optional[List[float]] = Field(default_factory=list)  
    nozzle_diameter: Optional[Dimension]
    chamber_build: Optional[ChamberBuild]  
    machine_batch_distance: Optional[Dimension]  
    build_rate: Optional[BuildRate] 
    max_printing_speed: Optional[Dimension]
    scan_speed: Optional[Dimension] 
    coating_time: Optional[float] 
    printing_speed: Optional[PrintingSpeed] 
    certificates: Optional[List[str]] = Field(default_factory=list)  # Added certificates field
    supported_input_file_formats: Optional[List[str]] = Field(default_factory=list)  # New field for supported file formats
    compatible_materials: Optional[List[str]] = Field(default_factory=list)
    support_materials: Optional[List[str]] = Field(default_factory=list)
    #loss_of_material: Optional[Dimension]
    #average_power_consumption: Optional[PowerConsumption]  




# Enumeration for printer module types
class ModuleType(str, Enum):
    """
    Enumeration for different module types in the 3D printing system.
    """
    printing = "Printing Module"  # Handles additive manufacturing
    post_curing = "Post-Curing Module"  # Used for curing materials post-printing
    mixing = "Mixing Module"  # For combining materials or technologies
    default = "Default Module"  # Fallback or unspecified module type
    curing = "Curing Module"  # Dedicated to curing prints
    inspection = "Inspection Module"  # Performs measurements or quality checks
    support_removal = "Support Material Removal Module"  # Removes supports from prints
    hybrid = "Hybrid Module"  # Combines multiple functionalities

# Enumeration for printer module types
class ConfigurationType(str, Enum):
    """
    Enumeration for different module types in the 3D printing system.
    """
    printing = "Printing Module"
    post_curing = "Post-Curing Module"
    mixing = "Mixing Module"
    default = "Default Module"




# Model for representing each printer module
class PrinterConfiguration(BaseModel):
    """Represents a printer module or the printer itself if standalone."""
    configuration_name: str # Name of the module or printer
    configuration_type: ConfigurationType
    physical_properties: PhysicalProperties = Field(default_factory=PhysicalProperties)  # Physical properties of the module
    specifications: PrinterSpecifications = Field(default_factory=PrinterSpecifications)  # Specifications of the module


# Updated PrinterModel to handle cases with or without modules
class PrinterModel(BaseModel):
    """Represents a collection of printer modules or standalone printer details."""
    printer_names: Optional[List[str]] = Field(default_factory=list)  # Main name of the printer
    #configuration_names: Optional[List[str]] = Field(default_factory=list)  
    configurations: Optional[List[PrinterConfiguration]] = Field(default_factory=list)  


    def is_standalone(self) -> bool:
        """Helper method to check if the printer is standalone (without modules)."""
        return len(self.configurations) == 0



# Aggregated response model for a 3D printer specification analysis
class PrinterResponse(BaseModel):
    """
    Aggregated response model for 3D printer data extraction.
    """
    organization: Organization
    printer_model: PrinterModel
    summary: str




##############################################################

class GeneralMaterialTypeEnum(str, Enum):
    """
    Enumeration for general material types.
    """
    polymer = "Polymer"
    photopolymer = "Photopolymer"
    metal = "Metal"
    ceramic = "Ceramic"
    composite = "Composite"
    sand = "Sand"
    wax = "Wax"
    other = "Other"


class PhotopolymerMaterialTypeEnum(str, Enum):
    """
    Enumeration for photopolymer material types.
    """
    acrylic = "Acrylic"
    acrylic_like = "Acrylic-like"
    epoxy = "Epoxy"
    oxycetane_resin = "Oxycetane Resin"
    polyurethane = "Polyurethane"
    resin = "Resin"
    silicon_like = "Silicon-like"
    other = "Other"

class PolymerMaterialTypeEnum(str, Enum):
    """Enumeration for polymer material types."""
    abs = "ABS"
    abs_pbt_like = "ABS/PBT-like"
    abs_pc = "ABS/PC"
    abs_pp = "ABS/PP"
    abs_pp_like = "ABS/PP-like"
    abs_like = "ABS-like"
    alumina_like = "Alumina-like"
    asa = "ASA"
    bvoh = "BVOH"
    ce_like = "CE-like"
    cpe = "CPE"
    gypsum = "Gypsum"
    hdpe_like = "HDPE-like"
    hips = "HIPS"
    pa = "PA"
    pa_tpe = "PA/TPE"
    paek = "PAEK"
    pa_glass = "PA-Glass"
    pa_like = "PA-like"
    pbt = "PBT"
    pc = "PC"
    pc_asa = "PC/ASA"
    pc_pbt = "PC/PBT"
    pc_ptfe = "PC/PTFE"
    pc_carbon = "PC/Carbon"
    pcl = "PCL"
    pc_like = "PC-like"
    pctg = "PCTG"
    pe = "PE"
    pe_pla = "PE/PLA"
    peba = "PEBA"
    peek = "PEEK"
    peek_like = "PEEK-like"
    pei = "PEI"
    pekk = "PEKK"
    pes = "PES"
    pet = "PET"
    pet_carbon = "PET-Carbon"
    petg = "PETG"
    pla = "PLA"
    pla_like = "PLA-like"
    pmma = "PMMA"
    pmma_like = "PMMA-like"
    pom_c = "POM-C"
    pp = "PP"
    pp_like = "PP-like"
    pps = "PPS"
    ppsu = "PPSU"
    ps = "PS"
    psu = "PSU"
    pva = "PVA"
    pvc = "PVC"
    pvdf = "PVDF"
    rubber_like = "Rubber-like"
    tpc = "TPC"
    tpe = "TPE"
    tpe_like = "TPE-like"
    tps = "TPS"
    tpu = "TPU"
    tpu_like = "TPU-like"
    wax_like = "Wax-like"
    wood_like = "Wood-like"
    other = "Other"

class CeramicMaterialTypeEnum(str, Enum):
    """Enumeration for ceramic material types."""
    alumina = "Alumina"
    glass = "Glass"
    gypsum_like = "Gypsum-like"
    ha = "HA"
    pa_carbon = "PA-Carbon"
    silicon_nitride = "Silicon Nitride"
    tcp = "TCP"
    tricalcium_phosphate = "Tricalcium Phosphate"
    zircon = "Zircon"
    zirconia = "Zirconia"
    other = "Other"


class MetalMaterialTypeEnum(str, Enum):
    """Enumeration for metal material types."""
    aluminum = "Aluminum"
    amorphous_metal = "Amorphous Metal"
    bronze = "Bronze"
    chromite = "Chromite"
    cobalt = "Cobalt"
    copper = "Copper"
    gold = "Gold"
    iridium = "Iridium"
    iron = "Iron"
    magnesium = "Magnesium"
    nickel = "Nickel"
    niobium = "Niobium"
    pa = "PA"  
    platinum = "Platinum"
    refractory_metal = "Refractory Metal"
    refractory_metal_bronze = "Refractory Metal, Bronze"
    silver = "Silver"
    steel = "Steel"
    tin = "Tin"
    titanium = "Titanium"
    tungsten = "Tungsten"
    zinc = "Zinc"
    zirconium = "Zirconium"
    other = "Other"

class CompositeMaterialTypeEnum(str, Enum):
    """Enumeration for composite material types."""
    abs_pc_carbon = "ABS/PC-Carbon"
    abs_pc_glass = "ABS/PC-Glass"
    abs_aramid = "ABS-Aramid"
    abs_carbon = "ABS-Carbon"
    abs_carbon_glass = "ABS/Carbon-Glass"
    abs_glass = "ABS/Glass"
    alumina = "Alumina"
    asa_carbon = "ASA-Carbon"
    carbon = "Carbon"
    carbon_nanotubes = "Carbon-Nanotubes"
    carbon_metal = "Carbon-Metal"
    carbon_metal_composite = "Carbon-Metal Composite"
    carbon_polymer = "Carbon-Polymer"
    carbon_silicone = "Carbon-Silicone"
    carbon_silicone_ceramic = "Carbon-Silicone-Ceramic"
    cermet = "Cermet"
    other = "Other"

class SandMaterialTypeEnum(str, Enum):
    """Enumeration for sand material types."""
    silicate = "Silicate"
    zircon = "Zircon"
    other = "Other"

class WaxMaterialTypeEnum(str, Enum):
    """Enumeration for wax material types."""
    wax = "Wax"
    wax_like = "Wax-like"
    other = "Other"

class SpecificMaterialTypeBase(BaseModel):
    general_material_type: Literal["Polymer", "Ceramic", "Metal", "Composite", "Sand", "Wax", "Other"]

class SpecificPolymerMaterialType(SpecificMaterialTypeBase):
    general_material_type: Literal["Polymer"]
    specific_material_type: PolymerMaterialTypeEnum

class SpecificPhotopolymerMaterialType(SpecificMaterialTypeBase):
    general_material_type: Literal["Photopolymer"]
    specific_material_type: PhotopolymerMaterialTypeEnum

class SpecificCeramicMaterialType(SpecificMaterialTypeBase):
    general_material_type: Literal["Ceramic"]
    specific_material_type: CeramicMaterialTypeEnum

class SpecificMetalMaterialType(SpecificMaterialTypeBase):
    general_material_type: Literal["Metal"]
    specific_material_type: MetalMaterialTypeEnum

class SpecificCompositeMaterialType(SpecificMaterialTypeBase):
    general_material_type: Literal["Composite"]
    specific_material_type: CompositeMaterialTypeEnum

class SpecificSandMaterialType(SpecificMaterialTypeBase):
    general_material_type: Literal["Sand"]
    specific_material_type: SandMaterialTypeEnum

class SpecificWaxMaterialType(SpecificMaterialTypeBase):
    general_material_type: Literal["Wax"]
    specific_material_type: WaxMaterialTypeEnum




class HardnessScaleEnum(str, Enum):
    """
    Enumeration for hardness scales.
    """
    shore_a = "Shore A"
    shore_b = "Shore B"
    shore_c = "Shore C"
    shore_d = "Shore D"
    shore_m = "Shore M"
    shore_r = "Shore R"
    not_reported = "Not reported"



class MaterialInformation(BaseModel):
    """
    Represents basic material information.
    """
    material_supplier: str 
    material_name: str
    compatible_printers: Optional[List[str]] = Field(default_factory=list)  # Added certificates field

    #material_description: Optional[str]  

    


class AdditiveManufacturingProcessEnum(str, Enum):
    """
    Enumeration for additive manufacturing processes.
    """
    binder_jetting = "Binder Jetting"
    directed_energy_deposition = "Directed Energy Deposition"
    material_extrusion = "Material Extrusion"
    material_jetting = "Material Jetting"
    powder_bed_fusion = "Powder Bed Fusion"
    sheet_lamination = "Sheet Lamination"
    vat_photopolymerization = "Vat Photopolymerization"
    not_reported = "Not reported"


class Range(BaseModel):
    value: float
    unit: str

class UltimateTensileStrength(BaseModel):
    value: float
    unit: str

class TensileModulus(BaseModel):
    value: float
    unit: str

class ElongationAtBreak(BaseModel):
    value: float
    unit: str 


class FlexuralStrength(BaseModel):
    value: float
    unit: str

class FlexuralModulus(BaseModel):
    value: float
    unit: str 

class ElongationModulus(BaseModel):
    value: float
    unit: str



class MechanicalProperties(BaseModel):
    """
    Represents the mechanical properties of the material.
    """
    ultimate_tensile_strength: Optional[UltimateTensileStrength]  
    tensile_modulus: Optional[TensileModulus]  
    elongation_modulus: Optional[ElongationModulus]  
    elongation_at_break: Optional[ElongationAtBreak] 
    elastic_modulus: Optional[TensileModulus] 
    flexural_strength: Optional[FlexuralStrength]  
    flexural_modulus: Optional[FlexuralModulus]  

class Hardness(BaseModel):
    """
    Represents the hardness properties of the material.
    """
    hardness_scale: HardnessScaleEnum


class HeatDeflectionTemperature(BaseModel):
    min: Range
    max: Range 



class ThermalProperties(BaseModel):
    """
    Represents the thermal properties of the material.
    """
    heat_deflection_temperature: HeatDeflectionTemperature
    glass_transition_temperature: Range

class PhysicalPropertiesMaterial(BaseModel):
    """
    Represents the physical properties of the material.
    """
    density: Optional[Range] 

class PrintingSettings(BaseModel):
    """
    Represents the physical properties of the material.
    """
    printing_speed: Optional[Range] 


class MaterialResponse(BaseModel):
    """
    Aggregates all material specification sections.
    """
    material_information: MaterialInformation
    am_process: Optional[AdditiveManufacturingProcessEnum] 
    certificates: Optional[List[str]] = Field(default_factory=list)  # Added certificates field
    material_type: Union[
        SpecificPolymerMaterialType,
        SpecificCeramicMaterialType,
        SpecificPhotopolymerMaterialType,
        SpecificMetalMaterialType,
        SpecificCompositeMaterialType,
        SpecificSandMaterialType,
        SpecificWaxMaterialType
    ]
    mechanical_properties: MechanicalProperties
    #hardness: Hardness
    #thermal_properties: ThermalProperties
    physical_properties: PhysicalPropertiesMaterial
    printing_settings: PrintingSettings 
    summary: str