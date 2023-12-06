"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for the sparql endpoint regarding 3D Printer Data
"""

import code_SemperKI.connections.cmem as SKICmem

########################################
# list of objects
getAllMaterials = SKICmem.ManageQueries("/Ontology/queries/material_Hannes")
getAllPrinters = SKICmem.ManageQueries("/Ontology/queries/printer_Hannes")