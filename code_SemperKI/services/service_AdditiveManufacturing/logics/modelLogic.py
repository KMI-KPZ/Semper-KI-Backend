from __future__ import annotations 
"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logics for model handling
"""

import logging, json, os, requests
import numpy as np
from stl import mesh
from io import BytesIO

from datetime import datetime

from django.conf import settings
from django.utils import timezone

from rest_framework import status

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.utilities.crypto import EncryptionAdapter

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.definitions import *
from code_SemperKI.logics.processLogics import updateProcessFunction
from code_SemperKI.utilities.basics import testPicture
from code_SemperKI.logics.filesLogics import logicForDeleteFile, getFileReadableStream
from code_SemperKI.logics.processLogics import updateProcessFunction

from ..definitions import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

#######################################################
def logicForUploadModelWithoutFile(validatedInput:dict, request) -> tuple[Exception, int]:
    """
    The logic for uploading a model without a file

    """

    try:
        content = ManageContent(request.session)
        interface = content.getCorrectInterface(updateProcessFunction.__name__) # if that fails, no files were uploaded and nothing happened
        if interface == None:
            return (Exception("Rights not sufficient in uploadModel"), 401)

        projectID = validatedInput[ProjectDescription.projectID]
        processID = validatedInput[ProcessDescription.processID]
        groupID = validatedInput["groupID"]
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
        
        # check if duplicates exist
        existingFileNames = set()
        processContent = interface.getProcess(projectID, processID)
        if isinstance(processContent, Exception):
            return (Exception(f"Process not found in {logicForUploadModelWithoutFile.__name__}"), 404)
        for key in processContent[ProcessDescription.files]:
            value = processContent[ProcessDescription.files][key]
            existingFileNames.add(value[FileObjectContent.fileName])

        fileID = crypto.generateURLFriendlyRandomString()
        modelToBeSaved = {}
        modelToBeSaved[FileObjectContent.id] = fileID
        modelToBeSaved[FileObjectContent.path] = ""
        modelToBeSaved[FileObjectContent.fileName] = validatedInput["name"]
        modelToBeSaved[FileObjectContent.imgPath] = ""
        modelToBeSaved[FileObjectContent.tags] = validatedInput["tags"] if "tags" in validatedInput["tags"] else []
        modelToBeSaved[FileObjectContent.licenses] = []
        modelToBeSaved[FileObjectContent.certificates] = []
        modelToBeSaved[FileObjectContent.quantity] = validatedInput["quantity"]
        modelToBeSaved[FileObjectContent.levelOfDetail] = validatedInput["levelOfDetail"]
        modelToBeSaved[FileObjectContent.isFile] = False
        modelToBeSaved[FileObjectContent.date] = str(timezone.now())
        modelToBeSaved[FileObjectContent.createdBy] = userName
        modelToBeSaved[FileObjectContent.createdByID] = content.getClient()
        modelToBeSaved[FileObjectContent.size] = 0
        modelToBeSaved[FileObjectContent.type] = FileTypes.Model
        modelToBeSaved[FileObjectContent.origin] = validatedInput["origin"]
        modelToBeSaved[FileObjectContent.remote] = False
        modelToBeSaved[FileContentsAM.width] = validatedInput["width"]
        modelToBeSaved[FileContentsAM.height] = validatedInput["height"]
        modelToBeSaved[FileContentsAM.length] = validatedInput["length"]
        modelToBeSaved[FileContentsAM.volume] = validatedInput["volume"] if "volume" in validatedInput else 0
        modelToBeSaved[FileContentsAM.complexity] = validatedInput["complexity"]
        modelToBeSaved[FileContentsAM.scalingFactor] = 1.0

        # calculate values right here
        calculationResult = calculateBoundaryDataForNonFileModel(modelToBeSaved)

        groups = interface.getProcess(projectID, processID)[ProcessDescription.serviceDetails][ServiceDetails.groups]
        changesArray = [{} for i in range(len(groups))]
        changesArray[groupID] = {ServiceDetails.models: {fileID: modelToBeSaved}, ServiceDetails.calculations: {fileID: calculationResult}}
        changes = {"changes": {ProcessUpdates.files: {fileID: modelToBeSaved}, ProcessUpdates.serviceDetails: {ServiceDetails.groups: changesArray}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            return (Exception("Rights not sufficient for logicForUploadModelWithoutFile"), 401)
        if isinstance(message, Exception):
            return (message, 500)
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},models,"+str(datetime.now()))

        return None, 200
    except Exception as e:
        loggerError.error("Error in logicForUploadModelWithoutFile: %s" % str(e))
        return (e, 500)
    
##################################################
def logicForUploadModel(validatedInput:dict, request) -> tuple[Exception, int]:
    """
    The logic for uploading a model

    """

    try:
        projectID = validatedInput[ProjectDescription.projectID]
        processID = validatedInput[ProcessDescription.processID]
        origin = validatedInput["origin"]
        groupID = validatedInput["groupID"]

        content = ManageContent(request.session)
        interface = content.getCorrectInterface(updateProcessFunction.__name__) # if that fails, no files were uploaded and nothing happened
        if interface is None:
            return (Exception("Rights not sufficient in uploadModel"), 401)
        
        if interface.checkIfFilesAreRemote(projectID, processID):
            remote = True
        else:
            remote = False
        
        detailsOfAllFiles = json.loads(validatedInput["details"])

        # TODO: if the file is a repo file, then create a local copy

        modelNames = list(request.FILES.keys())
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
        
        # check if duplicates exist
        existingFileNames = set()
        processContent = interface.getProcess(projectID, processID)
        if isinstance(processContent, Exception):
            return (Exception(f"Process not found in {logicForUploadModel.__name__}"), 404)
        for key in processContent[ProcessDescription.files]:
            value = processContent[ProcessDescription.files][key]
            existingFileNames.add(value[FileObjectContent.fileName])

        modelsToBeSaved = {}
        calculationsToBeSaved = {}
        for fileName in modelNames:
            # rename duplicates
            counterForFileName = 1
            nameOfFile = fileName
            while nameOfFile in existingFileNames:
                fileNameRoot, extension= os.path.splitext(nameOfFile)
                if counterForFileName > 100000:
                    return (Exception("Too many files with the same name uploaded!"), 400)
                
                if "_" in fileNameRoot:
                    fileNameRootSplit = fileNameRoot.split("_")
                    try:
                        counterForFileName = int(fileNameRootSplit[-1])
                        fileNameRoot = "_".join(fileNameRootSplit[:-1])
                        counterForFileName += 1
                    except:
                        pass
                nameOfFile = fileNameRoot + "_" + str(counterForFileName) + extension
                counterForFileName += 1
            for model in request.FILES.getlist(fileName):
                details = {}
                for detail in detailsOfAllFiles: # details are not in the same order as the models
                    if detail["fileName"] == fileName or detail["fileName"] == "file":
                        details = detail["details"]
                        break
                fileID = crypto.generateURLFriendlyRandomString()
                filePath = projectID+"/"+processID+"/"+fileID
                
                modelsToBeSaved[fileID] = {}
                modelsToBeSaved[fileID][FileObjectContent.id] = fileID
                modelsToBeSaved[fileID][FileObjectContent.path] = filePath
                modelsToBeSaved[fileID][FileObjectContent.fileName] = nameOfFile
                modelsToBeSaved[fileID][FileObjectContent.imgPath] = testPicture
                modelsToBeSaved[fileID][FileObjectContent.tags] = details["tags"]
                modelsToBeSaved[fileID][FileObjectContent.licenses] = details["licenses"]
                modelsToBeSaved[fileID][FileObjectContent.certificates] = details["certificates"]
                modelsToBeSaved[fileID][FileObjectContent.quantity] = details["quantity"] if "quantity" in details else 1
                modelsToBeSaved[fileID][FileObjectContent.levelOfDetail] = details["levelOfDetail"] if "levelOfDetail" in details else 1
                modelsToBeSaved[fileID][FileObjectContent.isFile] = True
                modelsToBeSaved[fileID][FileObjectContent.date] = str(timezone.now())
                modelsToBeSaved[fileID][FileObjectContent.createdBy] = userName
                modelsToBeSaved[fileID][FileObjectContent.createdByID] = content.getClient()
                modelsToBeSaved[fileID][FileObjectContent.size] = model.size
                modelsToBeSaved[fileID][FileObjectContent.type] = FileTypes.Model
                modelsToBeSaved[fileID][FileObjectContent.origin] = origin
                modelsToBeSaved[fileID][FileContentsAM.scalingFactor] = float(details["scalingFactor"]) if "scalingFactor" in details else 100.0
                
                # calculate values right here
                scalingFactor = modelsToBeSaved[fileID][FileContentsAM.scalingFactor]/100.
                result = calculateBoundaryData(model, nameOfFile, model.size, scalingFactor)
                if result["status_code"] != 200:
                    return (Exception(f"Error while calculating measurements for file {nameOfFile}"), 500)
                calculationsToBeSaved[fileID] = result
                
                if remote:
                    modelsToBeSaved[fileID][FileObjectContent.remote] = True
                    returnVal = s3.manageRemoteS3.uploadFile(filePath, model)
                    if returnVal is not True:
                        return (Exception(f"File {fileName} could not be saved to remote storage"), 500)
                else:
                    modelsToBeSaved[fileID][FileObjectContent.remote] = False
                    returnVal = s3.manageLocalS3.uploadFile(filePath, model)
                    if returnVal is not True:
                        return (Exception(f"File {fileName} could not be saved to local storage"), 500)

        groups = interface.getProcess(projectID, processID)[ProcessDescription.serviceDetails][ServiceDetails.groups]
        changesArray = [{} for i in range(len(groups))]
        changesArray[groupID] = {ServiceDetails.models: modelsToBeSaved, ServiceDetails.calculations: calculationsToBeSaved}
        changes = {"changes": {ProcessUpdates.files: modelsToBeSaved, ProcessUpdates.serviceDetails: {ServiceDetails.groups: changesArray}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            return (Exception("Rights not sufficient for uploadModels"), 401)
        if isinstance(message, Exception):
            return (message, 500)
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},models,"+str(datetime.now()))
        return None, 200
    except Exception as e:
        loggerError.error("Error in logicForUploadModel: %s" % str(e))
        return (e, 500)

##################################################
def logicForUpdateModel(request, validatedInput):
    """
    Update an existing model

    :param request: The request object
    :type request: Request
    :param validatedInput: The validated input
    :type validatedInput: Dict
    :return: Exception and status code
    :rtype: Tuple[Exception, int]

    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(updateProcessFunction.__name__)
        if interface == None:
            return (Exception("Rights not sufficient in updateModel"), 401)
        
        projectID = validatedInput[ProjectDescription.projectID]
        processID = validatedInput[ProcessDescription.processID]
        groupID = validatedInput["groupID"]
        fileID = validatedInput["id"]
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
        
        currentProcess = interface.getProcessObj(projectID, processID)
        modelsOfThisProcess = currentProcess.serviceDetails[ServiceDetails.groups][groupID][ServiceDetails.models]
        if fileID not in modelsOfThisProcess or fileID not in currentProcess.files:
            return (Exception("Model not found in updateModel"), 404)

        if currentProcess.client != contentManager.getClient():
            return (Exception("Rights not sufficient in updateModel"), 401)

        model = modelsOfThisProcess[fileID]

        # check if duplicates exist
        existingFileNames = set()
        processContent = interface.getProcess(projectID, processID)
        if isinstance(processContent, Exception):
            return (Exception(f"Process not found in {logicForUpdateModel.__name__}"), 404)
        for key in processContent[ProcessDescription.files]:
            value = processContent[ProcessDescription.files][key]
            if value[FileObjectContent.fileName] != model[FileObjectContent.fileName]:
                existingFileNames.add(value[FileObjectContent.fileName])
        
        # rename duplicates
        counterForFileName = 1
        nameOfFile = validatedInput["fileName"]
        while nameOfFile in existingFileNames:
            fileNameRoot, extension= os.path.splitext(nameOfFile)
            if counterForFileName > 100000:
                return (Exception("Too many files with the same name uploaded!"), 400)
            
            if "_" in fileNameRoot:
                fileNameRootSplit = fileNameRoot.split("_")
                try:
                    counterForFileName = int(fileNameRootSplit[-1])
                    fileNameRoot = "_".join(fileNameRootSplit[:-1])
                    counterForFileName += 1
                except:
                    pass
            nameOfFile = fileNameRoot + "_" + str(counterForFileName) + extension
            counterForFileName += 1
        
        
        model[FileObjectContent.fileName] = nameOfFile
        model[FileObjectContent.tags] = validatedInput["tags"] if "tags" in validatedInput else []
        model[FileObjectContent.licenses] = validatedInput["licenses"] if "licenses" in validatedInput else []
        model[FileObjectContent.certificates] = validatedInput["certificates"] if "certificates" in validatedInput else []
        model[FileObjectContent.quantity] = validatedInput["quantity"]
        model[FileObjectContent.levelOfDetail] = validatedInput["levelOfDetail"]
        model[FileObjectContent.isFile] = validatedInput["isFile"]
        if "width" in validatedInput:
            model[FileContentsAM.width] = validatedInput["width"]
        if "height" in validatedInput:
            model[FileContentsAM.height] = validatedInput["height"]
        if "length" in validatedInput:
            model[FileContentsAM.length] = validatedInput["length"]
        if "volume" in validatedInput:
            model[FileContentsAM.volume] = validatedInput["volume"]
        if "complexity" in validatedInput:
            model[FileContentsAM.complexity] = validatedInput["complexity"]
        if "scalingFactor" in validatedInput:
            model[FileContentsAM.scalingFactor] = validatedInput["scalingFactor"]
        

        # calculate values right here
        if model[FileObjectContent.isFile] is False:
            calculationResult = calculateBoundaryDataForNonFileModel(model)
        else:
            uploadedModel, flag = getFileReadableStream(request.session, projectID, processID, fileID)
            if flag is False:
                return (Exception(f"Error while accessing file {model[FileObjectContent.fileName]}"), 500)
            calculationResult = calculateBoundaryData(uploadedModel, nameOfFile, model[FileObjectContent.size], model[FileContentsAM.scalingFactor]/100.)

        groups = interface.getProcess(projectID, processID)[ProcessDescription.serviceDetails][ServiceDetails.groups]
        changesArray = [{} for i in range(len(groups))]
        changesArray[groupID] = {ServiceDetails.models: {fileID: model}, ServiceDetails.calculations: {fileID: calculationResult}}
        changes = {"changes": {ProcessUpdates.files: {fileID: model}, ProcessUpdates.serviceDetails: {ServiceDetails.groups: changesArray}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            return (Exception("Rights not sufficient for updateModel"), 401)
        if isinstance(message, Exception):
            return (message, 500)
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.EDITED},updated,{Logging.Object.OBJECT},model {fileID},"+str(datetime.now()))
        return None, 200
    except Exception as e:
        loggerError.error("Error in logicForUpdateModel: %s" % str(e))
        return (e, 500)

##################################################
def logicForDeleteModel(request, projectID, processID, groupID, fileID, functionName) -> tuple[Exception, int]:
    """
    The logic for deleting a model

    :param request: The request object
    :type request: Request
    :param projectID: The project ID
    :type projectID: str
    :param processID: The process ID
    :type processID: str
    :param groupID: The group ID
    :type groupID: int
    :param fileID: The file ID
    :type fileID: str
    :return: Exception and status code
    :rtype: tuple[Exception, int]
    
    """
    contentManager = ManageContent(request.session)
    interface = contentManager.getCorrectInterface(updateProcessFunction.__name__)
    if interface == None:
        return (Exception(f"Rights not sufficient in {functionName}"), 401)
        
    currentProcess = interface.getProcessObj(projectID, processID)
    modelsOfThisProcess = currentProcess.serviceDetails[ServiceDetails.groups][groupID][ServiceDetails.models]
    if fileID not in modelsOfThisProcess or fileID not in currentProcess.files:
        return (Exception(f"Model not found in {functionName}"), 404)

    if currentProcess.client != contentManager.getClient():
        return (Exception(f"Rights not sufficient in {functionName}"), 401)

    exception, statusCode = logicForDeleteFile(request, projectID, processID, fileID, functionName, True)
    if exception is not None:
        return (exception, statusCode)
    
    changesArray = [{} for i in range(len(currentProcess.serviceDetails[ServiceDetails.groups]))]
    changesArray[groupID] = {ServiceDetails.models: {fileID: None}}
    changes = {"changes": {}, "deletions": {ProcessUpdates.serviceDetails: {ServiceDetails.groups: changesArray}}}
    message, flag = updateProcessFunction(request, changes, projectID, [processID])
    if flag is False:
        return (Exception(f"Rights not sufficient in {functionName}"), 401)
    if isinstance(message, Exception):
        raise message

    logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},model {fileID}," + str(datetime.now()))        
    return None, 200


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

            fileContent, flag = getFileReadableStream(request.session, projectID, processID, model[FileObjectContent.id])
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