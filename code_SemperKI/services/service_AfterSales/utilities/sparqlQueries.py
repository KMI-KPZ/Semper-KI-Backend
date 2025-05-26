"""
Part of Semper-KI software

Silvio Weging 2023
Lukas Hein 2025

Contains: Services using the sparql endpoint regarding After Sales
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

########################################
# # list of Sparql queries
# getServiceProviders = SKICmem.ManageSPARQLQuery("/Ontology/queries/ServiceProvider_list_Hannes", parameters={SparqlParameters.ID: ""})
# createEntryForContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data insert/AddInfoForSP", post=True, parameters={SparqlParameters.ID: "", SparqlParameters.name: "", SparqlParameters.PrinterModel: "", SparqlParameters.Material: ""})
# updateEntryForContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data update/ServiceProvider_Hannes", post=True, parameters={SparqlParameters.ID: "", SparqlParameters.name: "", SparqlParameters.PrinterModel: "", SparqlParameters.Material: ""})
# deleteAllFromContractor = SKICmem.ManageSPARQLQuery("/Ontology/queries/Data delete/DeleteAllFromSP", post=True, parameters={SparqlParameters.ID: ""})