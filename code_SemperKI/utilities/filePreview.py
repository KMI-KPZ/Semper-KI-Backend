"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Functions to create, store and retrieve preview jpgs to uploaded files
"""
import logging, os
from multiprocessing import Process as MPProcess, Queue as MPQueue

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from Generic_Backend.code_General.connections.s3 import manageStaticsS3
from Generic_Backend.code_General.utilities.files import createFileResponse
from Generic_Backend.code_General.utilities.temporaryFolder import temporaryDirectory

from .basics import testPicture, previewNotAvailable, previewNotAvailableGER

loggerError = logging.getLogger("errors")
##################################################
try:
    from preview_generator.manager import PreviewManager

    ##################################################
    # def createPreviewInSeparateTask(temporaryFilePath:str, tempDir:str, resultQueue:MPQueue) -> None:
    #     """
    #     Create a preview of a file in a separate task
        
    #     """
    #     try:
    #         manager = PreviewManager(tempDir+"/previews", create_folder= True)
    #         result = manager.get_jpeg_preview(temporaryFilePath)
    #         resultQueue.put(result)
    #     except Exception as error:
    #         loggerError.error(f"Error while creating preview in separate task: {str(error)}")
    #         resultQueue.put(error)

    ##################################################
    def createAndStorePreview(file:InMemoryUploadedFile, fileName:str, locale:str, storagePath:str) -> str|Exception:
        """
        Create a preview of a file and store it in a given path
        
        """
        try:
            outPath = ""
            temporaryFileName = temporaryDirectory.createTemporaryFile(fileName, file.read())
            file.seek(0)
            #fileNameRoot, extension= os.path.splitext(file.name)
            basePath = storagePath+"_preview"+".jpg"
            remotePath = "public/previews/" + basePath
            outPath = settings.S3_STATIC_URL + "previews/" + basePath
            try:
                pathToPreviewImage = ""
                #resultQueue = MPQueue()
                #previewTask = MPProcess(target=createPreviewInSeparateTask, args=(temporaryFileName, tempDir, resultQueue))
                # TODO send this to another task since this can fail
                manager = PreviewManager(temporaryDirectory.getTemporaryFolderPath()+"/previews", create_folder= True)
                pathToPreviewImage = manager.get_jpeg_preview(temporaryFileName)
                #previewTask.start()
                #previewTask.join(60)
                #previewTask.close()
                #if not resultQueue.empty():
                    #path_to_preview_image = resultQueue.get()
                if isinstance(pathToPreviewImage, Exception):
                    raise pathToPreviewImage
                f = open(pathToPreviewImage, 'rb')
                manageStaticsS3.uploadFile(remotePath, f, True)
                f.close()
                temporaryDirectory.deleteTemporaryFile(fileName)
                os.remove(pathToPreviewImage)
                #else:
                    #raise Exception("Preview creation took too long")
            except Exception as _:
                if locale == "de-DE":
                    outPath = previewNotAvailableGER
                else:
                    outPath = previewNotAvailable
            return outPath
        except Exception as error:
            loggerError.error(f"Error while creating preview: {str(error)}")
            return error
    
    ##################################################
    def deletePreviewFile(path:str) -> None:
        """
        Deletes a preview file from the storage
        
        """
        try:
            if path == previewNotAvailableGER or path == previewNotAvailable:
                return
            pathInStorage = "public/" + path.replace(settings.S3_STATIC_URL, "")
            manageStaticsS3.deleteFile(pathInStorage)
        except Exception as error:
            loggerError.error(f"Error while deleting preview: {str(error)}")

except ImportError:
    # implement the same functions but as dummies that don't do anything
    ##################################################
    def createAndStorePreview(file:InMemoryUploadedFile, fileName:str, locale:str, storagePath:str) -> str|Exception:
        """
        Create a preview of a file and store it in a given path
        
        """
        if locale == "de-DE":
            return previewNotAvailableGER
        else:
            return previewNotAvailable
    ##################################################
    def deletePreviewFile(path:str) -> None:
        """
        Deletes a preview file from the storage
        
        """
        return