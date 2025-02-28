"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services using the sparql endpoint regarding Packaging
"""

import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

import code_SemperKI.connections.cmem as SKICmem

##################################################
class SparqlParameters(StrEnumExactlyAsDefined):
    """
    All parameters that could be important for a query. Not all are used every time.
    """
    ID = enum.auto()
    # name = enum.auto()
    # PrinterModel = enum.auto() 
    # Material = enum.auto()
    # min_length = enum.auto()
    # min_width = enum.auto()
    # min_height = enum.auto()

########################################
# # list of Sparql queries
# getAllMaterials = SKICmem.ManageSPARQLQuery("/Ontology/queries/material_Hannes")
# getAllPrinters = SKICmem.ManageSPARQLQuery("/Ontology/queries/printer_Hannes")
# getServiceProviders = SKICmem.ManageSPARQLQuery("/Ontology/queries/ServiceProvider_list_Hannes", parameters={SparqlParameters.ID: ""})
# createEntryForContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data insert/AddInfoForSP", post=True, parameters={SparqlParameters.ID: "", SparqlParameters.name: "", SparqlParameters.PrinterModel: "", SparqlParameters.Material: ""})
# updateEntryForContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data update/ServiceProvider_Hannes", post=True, parameters={SparqlParameters.ID: "", SparqlParameters.name: "", SparqlParameters.PrinterModel: "", SparqlParameters.Material: ""})
# deleteAllFromContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data delete/DeleteAllFromSP", post=True, parameters={SparqlParameters.ID: ""})
# deleteLinkPrinterMaterialOfContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data delete/DeleteLinkPrinterMaterial", post=True, parameters={SparqlParameters.ID: "", SparqlParameters.PrinterModel: "", SparqlParameters.Material: ""})
# deletePrinterOfContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data delete/DeletePrinterOfSP", post=True, parameters={SparqlParameters.ID: "", SparqlParameters.PrinterModel: ""})
# getManufacturersByBuildPlate = SKICmem.ManageSPARQLQuery("/Ontology/queries/serviceprovider_by_buildplate_Hannes",parameters={SparqlParameters.min_height: 0, SparqlParameters.min_length: 0, SparqlParameters.min_width: 0})
# getManufacturersByMaterial = SKICmem.ManageSPARQLQuery("/Ontology/queries/serviceprovider_by_material_Hannes")