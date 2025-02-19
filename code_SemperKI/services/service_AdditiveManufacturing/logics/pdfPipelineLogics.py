"""
Part of Semper-KI software

Silvio Weging, Mahdi Hedayat Mahmoudi 2024

Contains: Handler for processing pdfs to json
"""

import json, logging, copy, zipfile
from io import BytesIO
from difflib import SequenceMatcher
from datetime import datetime

from django.conf import settings

from llama_parse import LlamaParse
import fitz  # PyMuPDF for alternative text extraction
import pdfplumber  # For pdfplumber extraction

from Generic_Backend.code_General.definitions import *

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.modelFiles.nodesModel import NodeDescription, NodePropertiesTypesOfEntries, NodePropertyDescription
from code_SemperKI.connections.openai import callChatInterface
from code_SemperKI.connections.content.postgresql.pgKnowledgeGraph import Basics

from ..utilities.responseFormatsForPDFExtraction import PrinterResponse, MaterialResponse
from ..definitions import NodeTypesAM, NodePropertiesAMMaterial, NodePropertiesAMPrinter, NodePropertiesAMTechnology

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#######################################################
def extractTextWithLlamaparse(pdf_stream, fileName="derp.pdf"):
    """
    Extract text using LlamaParse.
    Uses AI to extract text from PDFs.
    
    """
    try:
        documents = LlamaParse(api_key=settings.LLAMA_CLOUD_API_KEY, result_type="text").load_data(pdf_stream, extra_info={"file_name": fileName})
        return "\n\n".join([doc.text for doc in documents]) if documents else None
    except Exception as e:
        logging.error(f"Error processing file {fileName} with LlamaParse: {e}")
        return None

#######################################################
def extractTextWithPymupdf(pdf_stream):
    """
    Extract text using PyMuPDF.
    Worst of the three
    
    """
    try:
        doc = fitz.open(stream=pdf_stream.read(), filetype="pdf")
        pdf_pages_content = ""
        for page_number in range(doc.page_count):
            page = doc[page_number]
            pdf_pages_content += page.get_text()
        return pdf_pages_content
    except Exception as e:
        logging.error(f"Error processing file with PyMuPDF: {e}")
        return None

#######################################################
def extractTextWithPdfplumber(pdf_stream):
    """
    Extract text using pdfplumber.
    Best using no AI
    
    """
    try:
        with pdfplumber.open(pdf_stream) as pdf:
            pdf_pages_content = ""
            for page in pdf.pages:
                pdf_pages_content += page.extract_text() or ""
        return pdf_pages_content.strip()  # Remove any extra whitespace
    except Exception as e:
        logging.error(f"Error processing file with pdfplumber: {e}")
        return None
    
#######################################################
def printerRole() -> str:
    """
    The role for the OpenAI chat interface for printer factsheets

    """
    return "You are a helpful assistant and expert in additive manufacturing. \
            Your task is to analyze factsheets about 3D printers and extract detailed data according to a defined schema. \
            The schema describes the following key attributes:\n\n \
            - organization: A dictionary that provides metadata about the organization associated with the 3D printer. It includes the following attributes:\
            - type: Specifies the role or category of the organization in the 3D printing ecosystem. \
                Examples include:\
                - 'manufacturer': If the organization designs, develops, and produces the 3D printer or its components.\n\
                - 'distributor': If the organization is responsible for selling or supplying the printer to customers but does not produce it.\n\
                - 'reseller': If the organization acts as an intermediary, purchasing from distributors or manufacturers and selling to end users.\n\
                - 'service provider': If the organization uses the printer for offering services like prototyping, manufacturing, or repairs.\n\
            - organization_name: The official name of the organization, typically matching its registered business name or brand.\n \
                Example: '3D Systems', 'Ultimaker', or 'Stratasys'.\n\
            - printer_model: A dictionary containing:\n\
              - printer_name: The name of all 3D printer models mentioned in the factsheet.\n\n\
              - configuration_names: A list of configuration names if multiple configuration/module exist for the 3d printer.\n\
              - configurations: A detailed list of printer configurations, where each configuration includes:\n\
                  - configuration_name: The name of the configuration or module.\n\
                  - configuration_type: The type of the configuration, which corresponds to a specific category or role in the 3D printing system. \
                    Use the following enumeration to classify types:\n\n\
                    - 'Printing Module': Handles additive manufacturing and material extrusion.\n\
                    - 'Post-Curing Module': Used for curing materials after printing.\n\
                    - 'Mixing Module': For combining materials or supporting multi-functional processes, such as laser engraving or CNC cutting.\n\
                    - 'Curing Module': Dedicated to curing prints, if reported separately from post-curing.\n\
                    - 'Inspection Module': Performs quality checks or measurements.\n\
                    - 'Support Material Removal Module': Removes support structures from printed models.\n\
                    - 'Hybrid Module': Combines multiple functionalities in a single module.\n\
                    - 'Default Module': Used as a fallback for unspecified or generic module types.\n\n\
                  - physical_properties: Physical characteristics such as weight and dimensions.\n\
                  - specifications: Technical details, including:\n\
                      - printing_technology: The type of 3D printing technology.\n\
                      - build_volume: Dimensions of the printable area (width, length, height).\n\
                      - layer_thickness: Minimum and maximum layer thickness values.\n\
                      - possible_layer_heights: A list of specific layer heights the printer supports.\n\
                      - nozzle_diameter: Diameter of the nozzle used for extrusion (if applicable).\n\
                      - chamber_build: Dimensions of the build chamber (if applicable).\n\
                      - machine_batch_distance: Batch distances during operation, if reported.\n\
                      - build_rate: Build rate, typically in cm³/h.\n\
                      - scan_speed: Scanning speed during the printing process, if applicable.\n\
                      - coating_time: Time taken for coating each layer, if available.\n\
                      - average_power_consumption: The average power consumption of the printer, typically reported in €/kWh.\n\
                      - compatible_materials: List of compatible printing materials.\n\
                      - support_materials: List of support materials.\n\n\
            - summary: A concise sentence summarizing the 3D printer's purpose or standout features.\n\n\
            The extracted data should follow this structured schema exactly, and incomplete or missing values should be \
            marked as null."


#######################################################
def parsePrinterJSONToDBKGFormat(jsonData:dict) -> list[dict]|Exception:
    """
    Insert JSON data from a printer into KG database format. Since printers have multiple configurations, an array is returned.
    
    :param jsonData: The extracted data from the factsheet
    :type jsonData: dict
    :param category: The category of the factsheet
    :type category: str
    :return: The data in KG format
    :rtype: list[dict]
    """
    try:
        outArray = []
        for key, value in jsonData.items():
            if key == "printer_model":
                for subKey, subValue in value.items():
                    if subKey == "configurations" and subValue is not None:
                        for config in subValue:
                            currentDict = {
                                NodeDescription.nodeType: NodeTypesAM.printer.value,
                                NodeDescription.context: jsonData.get("summary", ""),
                                NodeDescription.properties: []
                            }
                            currentDict[NodeDescription.nodeName] = jsonData.get("organization", {}).get("organization_name", "") + " " + jsonData.get("printer_model", {}).get("printer_names", [""])[0] + " " + config.get("configuration_name", "")
                            if "physical_properties" in config:
                                if "dimensions" in config["physical_properties"]:
                                    surfaceArea = config["physical_properties"].get("dimensions", {}).get("width", {}).get("value", 0) * config["physical_properties"].get("dimensions", {}).get("length", {}).get("value", 0) / 10000.0
                                    if surfaceArea > 0:
                                        currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.machineSurfaceArea, NodePropertyDescription.key: NodePropertiesAMPrinter.machineSurfaceArea, NodePropertyDescription.value: str(surfaceArea), NodePropertyDescription.unit: "m²", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                            if "specifications" in config:
                                itemsOfSpecifications = config["specifications"].items()
                                for specKey, specValue in itemsOfSpecifications:
                                    if specKey == "printing_technology" and specValue is not None and specValue != "":
                                        currentDict["technology"] = specValue
                                    elif specKey == "build_volume":
                                        currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.chamberBuildWidth, NodePropertyDescription.key: NodePropertiesAMPrinter.chamberBuildWidth, NodePropertyDescription.value: str(specValue.get("width", {}).get("value", 0)), NodePropertyDescription.unit: "mm", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                                        currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.chamberBuildLength, NodePropertyDescription.key: NodePropertiesAMPrinter.chamberBuildLength, NodePropertyDescription.value: str(specValue.get("length", 0).get("value", 0)), NodePropertyDescription.unit: "mm", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                                        currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.chamberBuildHeight, NodePropertyDescription.key: NodePropertiesAMPrinter.chamberBuildHeight, NodePropertyDescription.value: str(specValue.get("height", 0).get("value", 0)), NodePropertyDescription.unit: "mm", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                                    elif (specKey == "possible_layer_heights" or specKey == "layer_thickness") and specValue is not None and len(specValue) > 0:
                                        if specKey == "layer_thickness":
                                            if "possible_layer_heights" in itemsOfSpecifications and config["specifications"]["possible_layer_heights"] is not None and len(config["specifications"]["possible_layer_heights"]) > 0:
                                                continue # possible layer heights offers a better value
                                            if "max_thickness" in specValue and "min_thickness" in specValue and specValue["max_thickness"]["value"] is not None and specValue["max_thickness"]["unit"] == "µm" and specValue["min_thickness"]["value"] is not None and specValue["min_thickness"]["unit"] == "µm":
                                                currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.possibleLayerHeights, NodePropertyDescription.key: NodePropertiesAMPrinter.possibleLayerHeights, NodePropertyDescription.value: f'{str(specValue["max_thickness"]["value"])}, {str(specValue["min_thickness"]["value"])}', NodePropertyDescription.unit: "µm", NodePropertyDescription.type: NodePropertiesTypesOfEntries.text.value})
                                        else:
                                            currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.possibleLayerHeights, NodePropertyDescription.key: NodePropertiesAMPrinter.possibleLayerHeights, NodePropertyDescription.value: ",".join(map(str, specValue)), NodePropertyDescription.unit: "µm", NodePropertyDescription.type: NodePropertiesTypesOfEntries.text.value})
                                    elif specKey == "nozzle_diameter" and specValue is not None and specValue != "":
                                        currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.nozzleDiameter, NodePropertyDescription.key: NodePropertiesAMPrinter.nozzleDiameter, NodePropertyDescription.value: str(specValue.get("value", 0)), NodePropertyDescription.unit: "mm", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                                    elif specKey == "machine_batch_distance" and specValue is not None and specValue != "":
                                        currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.machineBatchDistance, NodePropertyDescription.key: NodePropertiesAMPrinter.machineBatchDistance, NodePropertyDescription.value: str(specValue.get("value", 0)), NodePropertyDescription.unit: "mm", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                                    elif specKey == "build_rate" and specValue is not None and specValue != "" and isinstance(specValue, dict):
                                        buildRate = None
                                        if "unit" in specValue:
                                            if specValue["unit"] == "cm³/h":
                                                buildRate = specValue["value"]
                                            elif specValue["unit"] == "cm³/min":
                                                buildRate = specValue["value"] * 60.
                                            elif specValue["unit"] == "cm³/s":
                                                buildRate = specValue["value"] * 3600.
                                            elif specValue["unit"] == "mm/h":
                                                buildRate = specValue["value"] / 1000.
                                            elif specValue["unit"] == "mm/s":
                                                buildRate = specValue["value"] * 3600. / 1000.
                                        if buildRate is not None:
                                            currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.buildRate, NodePropertyDescription.key: NodePropertiesAMPrinter.buildRate, NodePropertyDescription.value: str(buildRate), NodePropertyDescription.unit: "cm³/h", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                                    #elif specKey == "average_power_consumption" and specValue is not None and specValue != "":
                                    #    currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.averagePowerConsumption, NodePropertyDescription.key: NodePropertiesAMPrinter.averagePowerConsumption, NodePropertyDescription.value: str(specValue), NodePropertyDescription.unit: "€/kWh", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                                    elif (specKey == "printing_speed" or specValue == "max_printing_speed") and specValue is not None and specValue != "":
                                        printingSpeed = None
                                        if "unit" in specValue:
                                            if specValue["unit"] == "cm/h":
                                                printingSpeed = specValue["value"]
                                            elif specValue["unit"] == "m/s":
                                                printingSpeed = specValue["value"] * 360000.
                                            elif specValue["unit"] == "mm/s":
                                                printingSpeed = specValue["value"] * 360.
                                        if printingSpeed is not None:
                                            currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.maxPrintingSpeed, NodePropertyDescription.key: NodePropertiesAMPrinter.maxPrintingSpeed, NodePropertyDescription.value: str(specValue), NodePropertyDescription.unit: "cm/h", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                                    elif specKey == "certificates" and specValue is not None and len(specValue) > 0:
                                        currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.certificates, NodePropertyDescription.key: NodePropertiesAMPrinter.certificates, NodePropertyDescription.value: ",".join(specValue), NodePropertyDescription.unit: "", NodePropertyDescription.type: NodePropertiesTypesOfEntries.text.value})
                                    elif specKey == "coating_time" and specValue is not None and specValue != "":
                                        currentDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMPrinter.coatingTime, NodePropertyDescription.key: NodePropertiesAMPrinter.coatingTime, NodePropertyDescription.value: str(specValue), NodePropertyDescription.unit: "h", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                            outArray.append(currentDict)
        return outArray
    except Exception as e:
        loggerError.error(f"Error in parsePrinterJSONToDBKGFormat: {e}")
        return e


#######################################################
def parseMaterialJSONToDBKGFormat(jsonData:dict) -> dict|Exception:
    """
    Insert JSON data (one at a time) into KG database format
    
    :param jsonData: The extracted data from the factsheet
    :type jsonData: dict
    :param category: The category of the factsheet
    :type category: str
    :return: The data in KG format
    :rtype: dict
    """
    try:
        outDict = {
            NodeDescription.nodeType: NodeTypesAM.material.value,
            NodeDescription.context: jsonData.get("summary", ""),
            NodeDescription.properties: []
        }
        
        outDict[NodeDescription.nodeName] = jsonData.get("material_information", {}).get("material_supplier", "") + " " + jsonData.get("material_information", {}).get("material_name", "")
        for key, value in jsonData.items():
            if key == "certificates" and value is not None and len (value) > 0:
                outDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMMaterial.certificates, NodePropertyDescription.key: NodePropertiesAMMaterial.certificates, NodePropertyDescription.value: ",".join(value), NodePropertyDescription.unit: "", NodePropertyDescription.type: NodePropertiesTypesOfEntries.text.value})
            elif key == "mechanical_properties":
                for subKey, subValue in value.items():
                    if subKey == "ultimate_tensile_strength" and subValue is not None and subValue != "":
                        val = subValue.get("value", 0)
                        if subValue.get("unit", "") != "MPa":
                            if subValue.get("unit", "") == "GPa":
                                val = val * 1000
                            elif subValue.get("unit", "") == "kPa":
                                val = val / 1000
                            else:
                                val = 0
                        if val != 0:
                            outDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMMaterial.ultimateTensileStrength, NodePropertyDescription.key: NodePropertiesAMMaterial.ultimateTensileStrength, NodePropertyDescription.value: str(val), NodePropertyDescription.unit: "MPa", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                    elif (subKey == "tensile_modulus" or subKey == "youngs_modulus") and subValue is not None and subValue != "":
                        val = subValue.get("value", 0)
                        if subValue.get("unit", "") != "GPa":
                            if subValue.get("unit", "") == "MPa":
                                val = val / 1000
                            elif subValue.get("unit", "") == "kPa":
                                val = val / 1000000
                            else:
                                val = 0
                        if val != 0:
                            outDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMMaterial.tensileModulus, NodePropertyDescription.key: NodePropertiesAMMaterial.tensileModulus, NodePropertyDescription.value: str(val), NodePropertyDescription.unit: "GPa", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                    elif subKey == "elongation_at_break" and subValue is not None and subValue != "":
                        val = subValue.get("value", 0)
                        if subValue.get("unit", "") != "%":
                            val = 0
                        if val != 0:
                            outDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMMaterial.elongationAtBreak, NodePropertyDescription.key: NodePropertiesAMMaterial.elongationAtBreak, NodePropertyDescription.value: str(val), NodePropertyDescription.unit: "%", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                    elif subKey == "flexural_strength" and subValue is not None and subValue != "":
                        val = subValue.get("value", 0)
                        if subValue.get("unit", "") != "MPa":
                            if subValue.get("unit", "") == "GPa":
                                val = val * 1000
                            elif subValue.get("unit", "") == "kPa":
                                val = val / 1000
                            else:
                                val = 0
                        if val != 0:
                            outDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMMaterial.flexuralStrength, NodePropertyDescription.key: NodePropertiesAMMaterial.flexuralStrength, NodePropertyDescription.value: str(val), NodePropertyDescription.unit: "MPa", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                    elif subKey == "poisson_ratio" and subValue is not None and subValue != "":
                        outDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMMaterial.poissonRatio, NodePropertyDescription.key: NodePropertiesAMMaterial.poissonRatio, NodePropertyDescription.value: str(subValue), NodePropertyDescription.unit: "", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
                    elif subKey == "elastic_modulus" and subValue is not None and subValue != "":
                        val = subValue.get("value", 0)
                        if subValue.get("unit", "") != "GPa":
                            if subValue.get("unit", "") == "MPa":
                                val = val / 1000
                            elif subValue.get("unit", "") == "kPa":
                                val = val / 1000000
                            else:
                                val = 0
                        if val != 0:
                            outDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMMaterial.eModul, NodePropertyDescription.key: NodePropertiesAMMaterial.eModul, NodePropertyDescription.value: str(val), NodePropertyDescription.unit: "GPa", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
            elif key == "physical_properties":
                for subKey, subValue in value.items():
                    if subKey == "density" and subValue is not None and subValue != "":
                        if subValue.get("unit", "") == "g/cm³":
                            outDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMMaterial.density, NodePropertyDescription.key: NodePropertiesAMMaterial.density, NodePropertyDescription.value: str(subValue.get("value", 0)), NodePropertyDescription.unit: "g/cm³", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
            elif key == "printing_settings":
                for subKey, subValue in value.items():
                    if subKey == "printing_speed" and subValue is not None and subValue != "":
                            if subValue.get("unit", "") == "mm/s":
                                outDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMMaterial.printingSpeed, NodePropertyDescription.key: NodePropertiesAMMaterial.printingSpeed, NodePropertyDescription.value: str(value.get("printing_speed", 0)), NodePropertyDescription.unit: "mm/s", NodePropertyDescription.type: NodePropertiesTypesOfEntries.number.value})
            elif key == "material_type" and value is not None and len(value) > 0:
                if "general_material_type" in value and value["general_material_type"] is not None and value["general_material_type"] != "Other":
                    outDict["materialType"] = value["general_material_type"]
                if "specific_material_type" in value and value["specific_material_type"] is not None and value["specific_material_type"] != "Other":
                    outDict[NodeDescription.properties].append({NodePropertyDescription.name: NodePropertiesAMMaterial.specificMaterialType, NodePropertyDescription.key: NodePropertiesAMMaterial.specificMaterialType, NodePropertyDescription.value: str(value.get("specific_material_type", "")), NodePropertyDescription.unit: "", NodePropertyDescription.type: NodePropertiesTypesOfEntries.text.value})

        return outDict
    except Exception as e:
        loggerError.error(f"Error in parseMaterialJSONToDBKGFormat: {e}")
        return e
    
#######################################################
def insertIntoKG(dataDict:dict|list, category:str) -> None|Exception:
    """
    Insert extracted data into KG
    
    """
    try:
        if category == "printer":
            techNodes = Basics.getNodesByType(NodeTypesAM.technology.value)
            # go through all configurations
            for config in dataDict:
                # connect to existing technology node
                techID = ""
                if "technology" in config:
                    for tNode in techNodes:
                        similarity = SequenceMatcher(a=tNode[NodeDescription.nodeName], b=config["technology"]).quick_ratio()
                        if  similarity >= 0.8:
                            techID = tNode[NodeDescription.nodeID]
                            break
                    del config["technology"]
                createdPrinter = Basics.createNode(config)
                if isinstance(createdPrinter, Exception):
                    raise createdPrinter
                if techID != "":
                    Basics.createEdge(createdPrinter.nodeID, techID)
        elif category == "material":
            typeID = ""
            if "materialType" in dataDict:
                typeNodes = Basics.getNodesByType(NodeTypesAM.materialCategory.value)
                for tNode in typeNodes:
                    if SequenceMatcher(a=tNode[NodeDescription.nodeName], b=dataDict["materialType"]).quick_ratio() > 0.8:
                        typeID = tNode[NodeDescription.nodeID]
                        break
                del dataDict["materialType"]
                
            createdMaterial = Basics.createNode(dataDict)
            if isinstance(createdMaterial, Exception):
                raise createdMaterial
            if typeID != "":
                Basics.createEdge(createdMaterial.nodeID, typeID)
            # Create a specific material type node if it doesn't exist and connect it to the material node
            for prop in dataDict[NodeDescription.properties]:
                if prop[NodePropertyDescription.key] == NodePropertiesAMMaterial.specificMaterialType:
                    specificTypeNodes = Basics.getNodesByType(NodeTypesAM.materialType.value)
                    specificTypeNodeID = ""
                    for sNode in specificTypeNodes:
                        if SequenceMatcher(a=sNode[NodeDescription.nodeName], b=prop[NodePropertyDescription.value]).quick_ratio() > 0.8:
                            specificTypeNodeID = sNode[NodeDescription.nodeID]
                            break
                    if specificTypeNodeID == "":
                        specificTypeNode = Basics.createNode({NodeDescription.nodeType: NodeTypesAM.materialType.value, NodeDescription.nodeName: prop[NodePropertyDescription.value]})
                        if isinstance(specificTypeNode, Exception):
                            raise specificTypeNode
                        specificTypeNodeID = specificTypeNode.nodeID
                    Basics.createEdge(createdMaterial.nodeID, specificTypeNodeID)
    except Exception as e:
        loggerError.error(f"Error in insertIntoKG: {e}")
        return e

#######################################################
def convertAndInsertIntoKG(textContent:str, category:str, gptModel:str, insertIntoKGFlag:bool, listOfJSONs:list) -> None|Exception:
    """
    Do the rest
    
    """
    try:
        # Convert text to JSON
        if category == 'printer':
            jsonData = callChatInterface(gptModel, textContent, printerRole(), PrinterResponse)
        elif category == 'material':
            jsonData = callChatInterface(gptModel, textContent, "You are a helpful assistant and expert in additive manufacturing. Categorize & extract AM material specifications key info from a factsheet:", MaterialResponse)
        else:
            jsonData = {}
        if isinstance(jsonData, Exception):
            raise jsonData
        
        ####
        # Insert into KG
        if insertIntoKGFlag:
            if category == 'printer':
                resultDict = parsePrinterJSONToDBKGFormat(jsonData)
            elif category == 'material':
                resultDict = parseMaterialJSONToDBKGFormat(jsonData)
            else:
                resultDict = {}
            if isinstance(resultDict, Exception):
                raise resultDict
            result = insertIntoKG(resultDict, category)
            if isinstance(result, Exception):
                raise result

        listOfJSONs.append(jsonData)
    except Exception as error:
        loggerError.error(f"Error in convertAndInsertIntoKG: {error}")
        return error

#######################################################
def logicForPDFPipeline(validatedInput, files):
    """
    Logic for extracting data from uploaded pdf files
    
    """
    try:
        category = validatedInput["category"]
        if category not in ['printer', 'material']:
            raise Exception("Invalid category selected!")
        
        if "gptModel" in validatedInput and validatedInput["gptModel"] != "":
            gptModel = validatedInput["gptModel"]
        else:
            gptModel = "gpt-4o-mini"

        insertIntoKGFlag = validatedInput["insertIntoKG"]
        
        # gather uploaded file(s)
        listOfJSONs = []
        fileNames = list(files.keys())
        for fileName in fileNames:
            for file in files.getlist(fileName):
                # send to extraction pipeline

                # read file and extract text
                fileInBytes = BytesIO(file.read())

                # determine the file type
                if zipfile.is_zipfile(fileInBytes):
                    with zipfile.ZipFile(fileInBytes) as z:
                        for zFile in z.namelist():
                            if zFile.lower().endswith(".pdf"):
                                with z.open(zFile) as zF:
                                    textContent = extractTextWithPdfplumber(zF)
                                    if textContent is None:
                                        loggerError.error(f"Error extracting text from {zFile}")
                                        continue
                                    exception = convertAndInsertIntoKG(textContent, category, gptModel, insertIntoKGFlag, listOfJSONs)
                                    if isinstance(exception, Exception):
                                        loggerError.error(f"Error in convertAndInsertIntoKG: {exception}")
                                        continue
                            elif zFile.lower().endswith(".txt"):
                                with z.open(zFile) as zF:
                                    textContent = zF.read().decode("utf-8")
                                    if textContent is None:
                                        loggerError.error(f"Error extracting text from {zFile}")
                                        continue
                                    exception = convertAndInsertIntoKG(textContent, category, gptModel, insertIntoKGFlag, listOfJSONs)
                                    if isinstance(exception, Exception):
                                        loggerError.error(f"Error in convertAndInsertIntoKG: {exception}")
                                        continue
                elif file.name.lower().endswith(".pdf"):
                    textContent = extractTextWithPdfplumber(fileInBytes) #extractTextWithLlamaparse(fileInBytes, fileName)
                    if textContent is None:
                        loggerError.error(f"Error extracting text from {fileName}")
                        continue
                    exception = convertAndInsertIntoKG(textContent, category, gptModel, insertIntoKGFlag, listOfJSONs)
                    if isinstance(exception, Exception):
                        loggerError.error(f"Error in convertAndInsertIntoKG: {exception}")
                        continue
                elif file.name.lower().endswith(".txt"):
                    file.seek(0)
                    textContent = file.read().decode("utf-8")
                    if textContent is None:
                        loggerError.error(f"Error extracting text from {fileName}")
                        continue
                    exception = convertAndInsertIntoKG(textContent, category, gptModel, insertIntoKGFlag, listOfJSONs)
                    if isinstance(exception, Exception):
                        loggerError.error(f"Error in convertAndInsertIntoKG: {exception}")
                        continue
                else:
                    loggerError.error(f"Unsupported file type: {fileName}")

        return listOfJSONs, 200
    except Exception as e:
        loggerError.error(f"Error in logicForPDFPipeline: {e}")
        return e, 500
    
#######################################################
def logicForExtractFromJSON(validatedInput):
    """
    Logic for extracting data from JSON and add it to the KG
    
    """
    try:

        jsonData = validatedInput["data"]
        category = validatedInput["category"]
        
        for entry in jsonData:
            # Insert into KG
            if category == 'printer':
                resultDict = parsePrinterJSONToDBKGFormat(entry)
            elif category == 'material':
                resultDict = parseMaterialJSONToDBKGFormat(entry)
            else:
                resultDict = {}
            if isinstance(resultDict, Exception):
                raise resultDict
            result = insertIntoKG(resultDict, category)
            if isinstance(result, Exception):
                raise result

        
        return "Success", 200
    except Exception as e:
        loggerError.error(f"Error in logicForExtractFromJSON: {e}")
        return e, 500
