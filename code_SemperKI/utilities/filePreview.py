"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Functions to create, store and retrieve preview jpgs to uploaded files
"""
import io, logging, os, tempfile
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from Generic_Backend.code_General.connections.s3 import manageStaticsS3
from Generic_Backend.code_General.utilities.files import createFileResponse

from .basics import testPicture

loggerError = logging.getLogger("errors")
##################################################
try:
    from preview_generator.manager import PreviewManager
    from preview_generator.exception import UnsupportedMimeType

    ##################################################
    def createAndStorePreview(file:InMemoryUploadedFile, fileName:str, remote:bool, storagePath:str) -> str|Exception:
        """
        Create a preview of a file and store it in a given path
        
        """
        try:
            outPath = ""
            outError = ""
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
                except UnsupportedMimeType as _:
                    # TODO use token preview picture
                    outPath = testPicture
                except Exception as error:
                    outError = error # has to be done or else the temporary directory will not be deleted
            if isinstance(outError, Exception):
                raise outError
            return outPath
        except Exception as error:
            loggerError.error(f"Error while creating preview: {str(error)}")
            return error

except ImportError:
    # implement the same functions but as dummies that don't do anything
    def createAndStorePreview(file:BytesIO, fileName:str, remote:bool, storagePath:str) -> str|Exception:
        return testPicture