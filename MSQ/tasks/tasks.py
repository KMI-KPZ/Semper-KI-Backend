from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.utilities import crypto
from ..module.celery import app
from io import BytesIO
import pytetwild
import meshio
import numpy as np
from skfem import *
import tempfile

####################################################################
@app.task
def dummy(a:int,b:str):
    return (str(a)+b, dummy.__name__)

####################################################################
@app.task
def callfTetWild(inputFilePath:str):
    """
    Call fTetWild library to convert stl mesh to tetrahedral mesh

    :param inputFilePath: Path to STL file
    :type inputFilePath: str
    :return: The resulting mesh file
    :rtype: BytesIO file 
    
    """
    splitInput = inputFilePath.split("/")
    processID = splitInput[0]
    fileID = splitInput[1]
    local = True
    content, flag = s3.manageLocalS3.downloadFile(inputFilePath)
    if flag is False:
        local = False
        content, flag = s3.manageRemoteS3.downloadFile(inputFilePath)
        if flag is False:
            return ("", callfTetWild.__name__)
    # THIS IS BULLSHIT
    with tempfile.TemporaryDirectory() as tempDir:
        temporaryFileName = tempDir+"\\"+fileID+".stl"
        temporaryFile = open(temporaryFileName, 'wb')
        temporaryFile.write(content.getbuffer())
        temporaryFile.close()

        stl = meshio.read(temporaryFileName, file_format="stl")
        
        vertices, tetrahedras = pytetwild.tetrahedralize(stl.points, stl.cells_dict["triangle"])
        #p = np.array([vertices[:,0],  vertices[:,1],  vertices[:,2]], dtype=np.float64)
        #t = np.array(tetrahedras, dtype=np.float64).T
        #m = MeshTet(p, t)
        
        ####################################################################
        # This is only temporary, calculcation should be done here instead!
        cells = meshio.CellBlock('tetra', tetrahedras)
        tempFile = BytesIO()
        # outtypeArray =  ['mdpa', 'medit', 'su2', 'ugrid']
        meshio.write_points_cells(tempFile, vertices, [cells], file_format="ugrid")
        tempFile.seek(0)
        fileID = crypto.generateURLFriendlyRandomString()
        filePath = processID+"/"+fileID
        if local:
            returnVal = s3.manageLocalS3.uploadFile(filePath, tempFile)
        else:
            returnVal = s3.manageRemoteS3.uploadFile(filePath, tempFile)
        if returnVal is not True:
            return ("", callfTetWild.__name__)
        return (filePath, callfTetWild.__name__)
