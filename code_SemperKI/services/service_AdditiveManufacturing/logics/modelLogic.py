"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logics for model handling
"""

import logging
from datetime import datetime

from django.utils import timezone

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities import crypto

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.definitions import *
from code_SemperKI.handlers.public.process import updateProcessFunction

from ..definitions import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

#######################################################
def logicForUploadModelWithoutFile(validatedInput:dict, request):
    """
    The logic for uploading a model without a file

    """

    try:
        content = ManageContent(request.session)
        interface = content.getCorrectInterface(updateProcessFunction.__name__) # if that fails, no files were uploaded and nothing happened
        if interface == None:
            raise Exception("Rights not sufficient in uploadModel")

        projectID = validatedInput[ProjectDescription.projectID]
        processID = validatedInput[ProcessDescription.processID]
        userName = pgProfiles.ProfileManagementBase.getUserName(request.session)
        
        # check if duplicates exist
        existingFileNames = set()
        processContent = interface.getProcess(projectID, processID)
        if isinstance(processContent, Exception):
            raise Exception(f"Process not found in {logicForUploadModelWithoutFile.__name__}")
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

        fakeCalculation = {
            "filename": validatedInput["name"],
            "measurements": {
                "volume": float(modelToBeSaved[FileContentsAM.volume]),
                "surfaceArea": 0.0,
                "mbbDimensions": {
                    "_1": float(validatedInput["width"]),
                    "_2": float(validatedInput["length"]),
                    "_3": float(validatedInput["height"]),
                },
                "mbbVolume": float(validatedInput["width"]*validatedInput["length"]*validatedInput["height"]),
            },
            "status_code": 200
        }

        changes = {"changes": {ProcessUpdates.files: {fileID: modelToBeSaved}, ProcessUpdates.serviceDetails: {ServiceDetails.models: {fileID: modelToBeSaved}, ServiceDetails.calculations: {fileID: fakeCalculation}}}}

        # Save into files field of the process
        message, flag = updateProcessFunction(request, changes, projectID, [processID])
        if flag is False: # this should not happen
            raise Exception("Rights not sufficient for logicForUploadModelWithoutFile")
        if isinstance(message, Exception):
            raise message
        
        logger.info(f"{Logging.Subject.USER},{userName},{Logging.Predicate.CREATED},uploaded,{Logging.Object.OBJECT},models,"+str(datetime.now()))

    except Exception as e:
        loggerError.error("Error in logicForUploadModelWithoutFile: %s" % str(e))
        return e