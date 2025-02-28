"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Transform a STEP file to an STL file
"""
import logging, tempfile
import cadquery as cq
from cadquery import exporters
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

from Generic_Backend.code_General.definitions import FileObjectContent
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists

loggerError = logging.getLogger("errors")
##################################################
def transformSTPtoSTL(stpFile:InMemoryUploadedFile, fileName:str) -> BytesIO|Exception:
    """
    Transform a STEP file to an STL file

    :param stpFile: The STEP file
    :type stpFile: InMemoryUploadedFile
    :param fileName: The name of the file
    :type fileName: str
    :return: The STL file
    :rtype: BytesIO|Exception
    
    """
    try:
        stlContent = BytesIO()
        with tempfile.TemporaryDirectory() as tempDir:
            temporaryFileName = tempDir+"\\"+fileName
            fileName = fileName.split(".")[0] # remove the stp ending
            temporaryOutFileName = tempDir+"\\"+fileName+".stl"
            temporaryFile = open(temporaryFileName, 'wb')
            temporaryFile.write(stpFile.read())
            temporaryFile.close()
            cqStpfile = cq.importers.importStep(temporaryFileName)
            #assembly = cq.Assembly(cqStpfile)
            #cq.assembly.Assembly.save(assembly, temporaryOutFileName)
            exporters.export(cqStpfile, temporaryOutFileName)
            with open(temporaryOutFileName, 'rb') as stlFile:
                stlContent.write(stlFile.read())
            stlContent.seek(0)

        return stlContent
    except Exception as error:
        loggerError.error(f"Error while transforming STP to STL: {str(error)}")
        return error