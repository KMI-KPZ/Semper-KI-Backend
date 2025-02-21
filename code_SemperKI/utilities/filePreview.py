"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Functions to create, store and retrieve preview jpgs to uploaded files
"""
import io, logging, os, tempfile

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from Generic_Backend.code_General.connections.s3 import manageStaticsS3
from Generic_Backend.code_General.utilities.files import createFileResponse

from .basics import testPicture, previewNotAvailable, previewNotAvailableGER

loggerError = logging.getLogger("errors")
##################################################
try:
    from preview_generator.manager import PreviewManager

    ##################################################
    def createAndStorePreview(file:InMemoryUploadedFile, fileName:str, locale:str, storagePath:str) -> str|Exception:
        """
        Create a preview of a file and store it in a given path
        
        """
        try:
            outPath = ""
            with tempfile.TemporaryDirectory() as tempDir: # because meshio.read does not accept BytesIO, we have to use this bs
                manager = PreviewManager(tempDir+"/previews", create_folder= True)
                temporaryFileName = tempDir+"/"+fileName
                temporaryFile = open(temporaryFileName, 'wb')
                temporaryFile.write(file.read())
                file.seek(0)
                temporaryFile.close()
                #fileNameRoot, extension= os.path.splitext(file.name)
                basePath = storagePath+"_preview"+".jpg"
                remotePath = "public/previews/" + basePath
                outPath = settings.STATIC_URL + "previews/" + basePath
                try:
                    path_to_preview_image = manager.get_jpeg_preview(temporaryFileName)
                    f = open(path_to_preview_image, 'rb')
                    manageStaticsS3.uploadFile(remotePath, f, True)
                    f.close()
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
            manageStaticsS3.deleteFile(path)
        except Exception as error:
            loggerError.error(f"Error while deleting preview: {str(error)}")

except ImportError:
    # implement the same functions but as dummies that don't do anything
    ##################################################
    def createAndStorePreview(file:InMemoryUploadedFile, fileName:str, locale:str, storagePath:str) -> str|Exception:
        if locale == "de-DE":
            return previewNotAvailableGER
        else:
            return previewNotAvailable
    ##################################################
    def deletePreviewFile(path:str) -> None:
        return