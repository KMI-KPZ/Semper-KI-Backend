"""
Part of Semper-KI software

Silvio Weging, Mahdi Hedayat Mahmoudi 2024

Contains: Handler for processing pdfs to json
"""

from io import BytesIO
import json, logging, copy
from datetime import datetime
from django.conf import settings

from llama_parse import LlamaParse
import fitz  # PyMuPDF for alternative text extraction
import pdfplumber  # For pdfplumber extraction

from Generic_Backend.code_General.definitions import *

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.utilities.responseFormatsForPDFExtraction import PrinterResponse, MaterialResponse

from code_SemperKI.connections.openai import callChatInterface

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
        
        # gather uploaded file(s)
        listOfJSONs = []
        fileNames = list(files.keys())
        for fileName in fileNames:
            for file in files.getlist(fileName):
                # send to extraction pipeline

                # read file and extract text
                fileInBytes = BytesIO(file.read())
                textContent = extractTextWithPdfplumber(fileInBytes) #extractTextWithLlamaparse(fileInBytes, fileName)
                
                if textContent is None:
                    raise Exception("No text extracted from the PDF. Exiting.")

                # Convert text to JSON
                
                if category == 'printer':
                    jsonData = callChatInterface(gptModel, textContent, printerRole(), PrinterResponse)
                elif category == 'material':
                    jsonData = callChatInterface(gptModel, textContent, "You are a helpful assistant and expert in additive manufacturing. Categorize & extract AM material specifications key info from a factsheet:", MaterialResponse)
                else:
                    jsonData = {}
                if isinstance(jsonData, Exception):
                    raise jsonData
                listOfJSONs.append(jsonData)

        return listOfJSONs, 200
    except Exception as e:
        loggerError.error(f"Error in logicForPDFPipeline: {e}")
        return e, 500