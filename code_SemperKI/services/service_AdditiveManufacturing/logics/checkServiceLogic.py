"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logic for the Additive Manufacturing service checking
"""
import logging, requests
import numpy as np
from stl import mesh
from io import BytesIO

from django.conf import settings

from rest_framework import status

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists
from Generic_Backend.code_General.definitions import FileObjectContent
from Generic_Backend.code_General.utilities.crypto import EncryptionAdapter

from code_SemperKI.definitions import *
from code_SemperKI.handlers.public.files import getFileReadableStream
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.handlers.public.process import updateProcessFunction

from ..definitions import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")



####################################################################################

#######################################################
def getBoundaryData(readableObject, fileName:str = "ein-dateiname.stl") -> dict:
    """
    Send the model to the Chemnitz service and get the dimensions

    :param readableObject: The model to be sent to the service with a .read() method
    :type readableObject: BytesIO | EncryptionAdapter
    :param filename: The file name
    :type filename: str
    :return: data obtained by IWU service
    :rtype: Dict

    """

    result =  {"status_code": 500, "content": {"error": "Fehler"}}

    url = settings.IWS_ENDPOINT + "/properties"
    headers = {'Content-Type': 'model/stl','content-disposition' : f'filename="{fileName}"'}

    try:
        response = requests.post(url, data=readableObject, headers=headers, stream=True)
    except Exception as e:
        logger.warning(f"Error while sending model to Chemnitz service: {str(e)}")
        return {"status_code" : 500, "content": {"error": "Fehler"}}

    # Check the response
    if response.status_code == 200:
        logger.info(f"Success capturing measurements from Chemnitz service")
        result = response.json()
        result["status_code"] = 200

    return result

##################################################
def calculateBoundaryData(readableObject:EncryptionAdapter, fileName:str, fileSize:int, scalingFactor:float) -> dict:
    """
    Calculate some of the stuff ourselves

    :param readableObject: The model to be sent to the service with a .read() method
    :type readableObject: BytesIO | EncryptionAdapter
    :param filename: The file name
    :type filename: str
    :param fileSize: The size of the file  
    :type fileSize: int
    :return: data obtained by IWU service
    :rtype: Dict
    
    """
    try:
        completeFile = readableObject.read(fileSize)
        fileAsBytesObject = BytesIO(completeFile)
        your_mesh = mesh.Mesh.from_file(fileName, fh=fileAsBytesObject)
        volume, _, _ = your_mesh.get_mass_properties()
    
        # Calculate the surface area by summing up the area of all triangles
        surface_area = np.sum(your_mesh.areas)
        
        # Calculate the bounding box
        min_bound = np.min(your_mesh.points.reshape(-1, 3), axis=0)
        max_bound = np.max(your_mesh.points.reshape(-1, 3), axis=0)
        bounding_box = max_bound - min_bound
        volumeBB = bounding_box[0]*bounding_box[1]*bounding_box[2]
        scalingFactorTimesThree = scalingFactor*scalingFactor*scalingFactor

        result = {
                "filename": fileName,
                "measurements": {
                    "volume": float(volume)*scalingFactorTimesThree,
                    "surfaceArea": float(surface_area)*scalingFactor*scalingFactor,
                    "mbbDimensions": {
                        "_1": float(bounding_box[0])*scalingFactor,
                        "_2": float(bounding_box[1])*scalingFactor,
                        "_3": float(bounding_box[2])*scalingFactor,
                    },
                    "mbbVolume": float(volumeBB)* scalingFactorTimesThree,
                },
                "status_code": 200
            }
        return result
    except Exception as error:
        loggerError.error(f"Error while calculating measurements: {str(error)}")
        return {"status_code" : 500, "content": {"error": error}}

#######################################################
def calculateBoundaryDataForNonFileModel(model:dict) -> dict:
    """
    Calculate the same stuff as above but for a model that is not a file

    :param model: The model 
    :type model: Dict
    :return: data in IWU format
    :rtype: Dict
    
    """
    fakeCalculation = {
            "filename": model[FileObjectContent.fileName],
            "measurements": {
                "volume": float(model[FileContentsAM.volume]),
                "surfaceArea": 0.0,
                "mbbDimensions": {
                    "_1": float(model[FileContentsAM.width]),
                    "_2": float(model[FileContentsAM.length]),
                    "_3": float(model[FileContentsAM.height]),
                },
                "mbbVolume": float(model[FileContentsAM.width]*model[FileContentsAM.length]*model[FileContentsAM.height]),
            },
            "status_code": 200
        }
    return fakeCalculation

##################################################
def logicForCheckModel(request, functionName:str, projectID:str, processID:str, fileID:str) -> tuple[dict|Exception, int]:
    """
    Calculate model properties like boundary and volume

    :param request: GET Request
    :type request: HTTP GET
    :param functionName: The name of the function
    :type functionName: str
    :param projectID: The project ID
    :type projectID: str
    :param processID: The process ID
    :type processID: str
    :param fileID: The file ID
    :type fileID: str
    :return: dict with calculations or an exception and status code
    :rtype: Tuple[Dict, int]
    
    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(functionName)
        if interface == None:
            return (Exception(f"Rights not sufficient in {functionName}"), 401)
            
        process = interface.getProcessObj(projectID, processID)
        if isinstance(process, Exception):
            return (Exception(f"process not found in {functionName}"), 404)
            
        
        # If calculations are already there, take these, unless they are mocked
        model = {}
        groupWhereTheModelLies = 0
        for idx, group in enumerate(process.serviceDetails[ServiceDetails.groups]):
            if ServiceDetails.models in group:
                if fileID in group[ServiceDetails.models]:
                    model = group[ServiceDetails.models][fileID]
                    groupWhereTheModelLies = idx
                    break

        
        scalingFactor = model[FileContentsAM.scalingFactor]/100. if FileContentsAM.scalingFactor in model else 1.0

        if model[FileObjectContent.isFile] is True:
            modelName = model[FileObjectContent.fileName]

            mock = {
                "filename": modelName,
                "measurements": {
                    "volume": -1.0,
                    "surfaceArea": -1.0,
                    "mbbDimensions": {
                        "_1": -1.0,
                        "_2": -1.0,
                        "_3": -1.0,
                    },
                    "mbbVolume": -1.0,
                },
                "status_code": 200
            }

            # if settings.IWS_ENDPOINT is None:
            #     outputSerializer = SResCheckModel(data=mock)
            #     if outputSerializer.is_valid():
            #         return Response(outputSerializer.data, status=status.HTTP_200_OK)
            #     else:
            #         raise Exception("Validation failed")

            fileContent, flag = getFileReadableStream(request, projectID, processID, model[FileObjectContent.id])
            if flag:
                resultData = calculateBoundaryData(fileContent, modelName, model[FileObjectContent.size], scalingFactor) # getBoundaryData(fileContent, modelName)
            else:
                return (Exception(f"Error while accessing file {modelName}"), 500)

            if resultData["status_code"] != 200:
                return (mock, 200)
        else:
            resultData = calculateBoundaryDataForNonFileModel(model)
        
        # save results in model file details
        groupArray = [{} for i in range(len(process.serviceDetails[ServiceDetails.groups]))]
        groupArray[groupWhereTheModelLies] = {ServiceDetails.calculations: {fileID: resultData}}
        changes = {"changes": {ProcessUpdates.serviceDetails: {ServiceDetails.groups: groupArray}}}
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False:
            return (Exception(f"Rights not sufficient in {functionName} while updating process"), 401)
        if isinstance(message, Exception):
            raise message
        
        return resultData, 200
    except Exception as e:
        loggerError.error(f"Error in {functionName}: {str(e)}")
        return (e, 500)
