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
from Generic_Backend.code_General.utilities.temporaryFolder import temporaryDirectory

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
        fileName = fileName.split(".")[0] # remove the stp ending
        temporaryFileName = temporaryDirectory.createTemporaryFile(fileName+".stp", stpFile.read())
        cqStpfile = cq.importers.importStep(temporaryFileName)
        #assembly = cq.Assembly(cqStpfile)
        #cq.assembly.Assembly.save(assembly, temporaryOutFileName)
        stlContent = BytesIO()
        tempDir = temporaryDirectory.getTemporaryFolderPath()
        temporaryOutFileName = tempDir+"/"+fileName+".stl"
        exporters.export(cqStpfile, temporaryOutFileName)
        with open(temporaryOutFileName, 'rb') as stlFile:
            stlContent.write(stlFile.read())
        stlContent.seek(0)
        temporaryDirectory.deleteTemporaryFile(fileName+".stp")
        return stlContent
    except Exception as error:
        loggerError.error(f"Error while transforming STP to STL: {str(error)}")
        return error