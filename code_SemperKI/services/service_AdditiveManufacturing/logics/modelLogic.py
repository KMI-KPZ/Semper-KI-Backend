"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logics for model handling
"""

import logging, json, os
from datetime import datetime

from django.utils import timezone

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections import s3

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.definitions import *
from code_SemperKI.handlers.public.process import updateProcessFunction
from code_SemperKI.utilities.basics import testPicture

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

        changes = {"changes": {ProcessUpdates.files: {fileID: modelToBeSaved}, ProcessUpdates.serviceDetails: {ServiceDetails.models: {fileID: modelToBeSaved}}}}

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
                
        changes = {"changes": {ProcessUpdates.files: modelsToBeSaved, ProcessUpdates.serviceDetails: {ServiceDetails.models: modelsToBeSaved}}}

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