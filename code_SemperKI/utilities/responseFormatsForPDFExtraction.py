"""
Part of Semper-KI software

Silvio Weging, Mahdi Hedayat Mahmoudi 2024

Contains: Definitions to how the chat model should extract data
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal

# Enumeration of 3D printer types
class PrinterType(str, Enum):
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
    manufacturer = "manufacturer"
    distributor = "distributor"
    service_provider = "service_provider"
    research_institution = "research_institution"
    other = "other"

# Model representing an organization
class Organization(BaseModel):
    type: OrganizationType
    name: str

class PrinterModel(BaseModel):
    name: str

class Dimension(BaseModel):
    value: float
    unit: str


class BuildVolume(BaseModel):
    width: Dimension
    length: Dimension
    height: Dimension

# Model representing printer specifications
class PrinterSpecification(BaseModel):
    printing_technology: PrinterType
    build_volume: BuildVolume
    compatible_material: Optional[List[str]] = Field(default_factory=list)  # Default to empty list if missing
    support_material: Optional[List[str]] = Field(default_factory=list)  # Default to empty list if missing


# Aggregated response model for a 3D printer specification analysis
class PrinterResponse(BaseModel):
    organization: Organization
    printer_model: PrinterModel
    printer_specifications: PrinterSpecification
    summary: str





##############################################################

class GeneralMaterialTypeEnum(str, Enum):
    """
    Enumeration for general material types.
    """
    polymer = "Polymer"
    metal = "Metal"
    ceramic = "Ceramic"
    composite = "Composite"
    sand = "Sand"
    wax = "Wax"
    other = "Other"




class PolymerMaterialTypeEnum(str, Enum):
    """Enumeration for polymer material types."""
    abs = "ABS"
    abs_pbt_like = "ABS/PBT-like"
    abs_pc = "ABS/PC"
    abs_pp = "ABS/PP"
    abs_pp_like = "ABS/PP-like"
    abs_like = "ABS-like"
    acrylic = "Acrylic"
    acrylic_like = "Acrylic-like"
    alumina_like = "Alumina-like"
    asa = "ASA"
    bvoh = "BVOH"
    ce_like = "CE-like"
    cpe = "CPE"
    epoxy = "Epoxy"
    gypsum = "Gypsum"
    hdpe_like = "HDPE-like"
    hips = "HIPS"
    oxycetane_resin = "Oxycetane Resin"
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
    resin = "Resin"
    rubber_like = "Rubber-like"
    silicon_like = "Silicon-like"
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
    pa = "PA"  # Clarify the full form of "PA" if necessary.
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
    material_description: Optional[str]  

    


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
    min: Range
    max: Range

class TensileModulus(BaseModel):
    min: Range
    max: Range

class ElongationAtBreak(BaseModel):
    min: Range
    max: Range 


class FlexuralStrengthk(BaseModel):
    min: Range
    max: Range 

class FlexuralModulus(BaseModel):
    min: Range
    max: Range 


class MechanicalProperties(BaseModel):
    """
    Represents the mechanical properties of the material.
    """
    ultimate_tensile_strength: UltimateTensileStrength
    tensile_modulus: TensileModulus
    elongation_at_break: ElongationAtBreak
    flexural_strength: FlexuralStrengthk
    flexural_modulus: FlexuralModulus

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

class PhysicalProperties(BaseModel):
    """
    Represents the physical properties of the material.
    """
    min_part_density: Range

class MaterialResponse(BaseModel):
    """
    Aggregates all material specification sections.
    """
    material_information: MaterialInformation
    am_process: AdditiveManufacturingProcessEnum
    material_type: str
    material_type: Union[
        SpecificPolymerMaterialType,
        SpecificCeramicMaterialType,
        SpecificMetalMaterialType,
        SpecificCompositeMaterialType,
        SpecificSandMaterialType,
        SpecificWaxMaterialType
    ]
    mechanical_properties: MechanicalProperties
    #hardness: Hardness
    #thermal_properties: ThermalProperties
    physical_properties: PhysicalProperties
    summary: str
