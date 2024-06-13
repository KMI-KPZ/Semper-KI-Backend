"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services using the sparql endpoint regarding 3D Printer Data
"""

import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactylAsDefined

import code_SemperKI.connections.cmem as SKICmem

##################################################
class SparqlParameters(StrEnumExactylAsDefined):
    """
    All parameters that could be important for a query. Not all are used every time.
    """
    ID = enum.auto()
    name = enum.auto()
    PrinterModel = enum.auto() 
    Material = enum.auto()

########################################
# list of Sparql queries
getAllMaterials = SKICmem.ManageSPARQLQuery("/Ontology/queries/material_Hannes")
getAllPrinters = SKICmem.ManageSPARQLQuery("/Ontology/queries/printer_Hannes")
getServiceProviders = SKICmem.ManageSPARQLQuery("/Ontology/queries/ServiceProvider_list_Hannes")
createEntryForContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data insert/ServiceProvider_Hannes", post=True, parameters={SparqlParameters.ID: "", SparqlParameters.name: "", SparqlParameters.PrinterModel: "", SparqlParameters.Material: ""})
updateEntryForContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data update/ServiceProvider_Hannes", post=True, parameters={SparqlParameters.ID: "", SparqlParameters.name: "", SparqlParameters.PrinterModel: "", SparqlParameters.Material: ""})
deleteEntryForContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data delete/ServiceProvider_Hannes", post=True, parameters={SparqlParameters.ID: ""})
filterByBuildPlate = SKICmem.ManageSPARQLQuery("",parameters={})
