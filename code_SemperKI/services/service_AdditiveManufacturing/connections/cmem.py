"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for the sparql endpoint regarding 3D Printer Data
"""

import code_SemperKI.connections.cmem as SKICmem
from code_General.utilities.sparql import SparqlResource,SparqlQueryManager,QueryType



#######################################################

class AdditiveQueryManager(SparqlQueryManager):
    material: SparqlResource = {QueryType.GET: "/Ontology/queries/material_Hannes"}
    printer: SparqlResource = {QueryType.GET: "/Ontology/queries/printer_Hannes"}
    serviceProvider: SparqlResource = { QueryType.GET:"/Ontology/queries/ServiceProvider_list_Hannes",
                                        QueryType.INSERT:"/Ontology/queries/Data insert/ServiceProvider_Hannes",
                                        QueryType.DELETE:"/Ontology/queries/Data delete/ServiceProvider_Hannes",}
    manufacturer: SparqlResource = { QueryType.GET:"/Ontology/queries/manufacturer_Hannes"}

########################################
# list of objects
getAllMaterials = SKICmem.ManageQueries("/Ontology/queries/material_Hannes")
getAllPrinters = SKICmem.ManageQueries("/Ontology/queries/printer_Hannes")