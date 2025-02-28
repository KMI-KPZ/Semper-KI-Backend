"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling test calls
"""
import platform, subprocess, json, requests, io, logging, os, tempfile, zipfile
from io import BytesIO

from django.http import HttpResponse, JsonResponse, FileResponse

from Generic_Backend.code_General.utilities.files import createFileResponse

from code_SemperKI.utilities.serializer import ExceptionSerializer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from drf_spectacular.utils import extend_schema
from rest_framework.views import exception_handler

loggerError = logging.getLogger("errors")
#####################################################################
# @api_view(['GET'])
# def restTest(request, dummy:str):
#     if request.method == "GET":
#         return Response("Test "+dummy, status=status.HTTP_200_OK)
    
class restTestAPI(APIView):

    class RequestSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)
        age = serializers.IntegerField(min_value=18)
        
    class ResponseSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)
        age = serializers.IntegerField(min_value=18)
        dummy = serializers.CharField(max_length=100)

    @extend_schema(
        operation_id="test",
        summary="Test",
        description="Test",
        responses={
            200: ResponseSerializer
        },
    )
    def get(self, request, dummy:str, format=None):
        return Response({"name": "test", "age": 12, "dummy": dummy}, status=status.HTTP_200_OK)
    
    @extend_schema(
        operation_id="test2",
        summary="Test2",
        description="Test2",
        request=RequestSerializer,
        responses={
            200: ResponseSerializer,
            400: ExceptionSerializer
        },
    )
    def post(self, request, dummy:str, format=None):
        json_data=request.body
        stream= io.BytesIO(json_data)
        jsonContent = JSONParser().parse(stream)
        serializer = self.RequestSerializer(data=jsonContent)
        if serializer.is_valid():
            validatedInput = serializer.data
            validatedInput["dummy"]=dummy
            outSerializer = self.ResponseSerializer(validatedInput)
            output = JSONRenderer().render(outSerializer.data)
            return Response(output, status=status.HTTP_200_OK)
        else:
            exceptionSerializer = ExceptionSerializer(serializer.errors)
            return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)


import io, time
from stl import mesh
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot
import numpy as np
from PIL import Image
import base64

def find_mins_maxs(obj):
    minx = obj.x.min()
    maxx = obj.x.max()
    miny = obj.y.min()
    maxy = obj.y.max()
    minz = obj.z.min()
    maxz = obj.z.max()
    return minx, maxx, miny, maxy, minz, maxz
#######################################################
def stlToBinJpg(file) -> str:
    """
    Convert stl file to jpg

    :param file: open file from redis
    :type file: binary file
    :return: jpg for rendering
    :rtype: JPG as base64 encoded binary string
    
    """
    try:
        # Create a new plot
        px = 1/pyplot.rcParams['figure.dpi']
        figure = pyplot.figure(figsize=(320*px,320*px), layout='tight')
        axes = figure.add_subplot(projection='3d')
        axes.grid(False)
        axes.axis('off')
        axes.dist = 5.5 # distance of the camera to the object, defined in Axes3D
    
        # Load the STL files and add the vectors to the plot
        your_mesh = mesh.Mesh.from_file("",fh=file)
        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))
    
        # Auto scale to the mesh size
        scale = your_mesh.points.flatten()
        axes.auto_scale_xyz(scale, scale, scale)
    
        #pyplot.savefig("test.jpg", format="jpg", bbox_inches='tight', pad_inches = 0)
        # Save file into binary string
        figure.canvas.draw()
        data = np.frombuffer(figure.canvas.tostring_rgb(), dtype=np.uint8)
        data = data.reshape(figure.canvas.get_width_height()[::-1] + (3,))
        img = Image.fromarray(data)
        
        convertedJpg = io.BytesIO()
        # pyplot.savefig(convertedJpg, format="jpg", bbox_inches='tight', pad_inches = 0) # too slow
        img.save(convertedJpg, format="jpeg")
        return base64.b64encode(convertedJpg.getvalue())
    except (Exception) as error:
        loggerError.error(f"Error while converting stl to jpg: {str(error)}")
        return base64.b64encode(error)


#######################################################
class SReqUploadTestFiles(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField())
##################################################
@extend_schema(
     summary="File upload for a process",
     description=" ",
     request={
        "multipart/form-data": SReqUploadTestFiles
    },
     tags=['Test - Files'],
     responses={
         200: None,
         401: ExceptionSerializer,
         500: ExceptionSerializer
     }
 )
@api_view(['POST'])
def testPreview(request:Request):
    from preview_generator.manager import PreviewManager
    from preview_generator.exception import UnsupportedMimeType
    inSerializer = SReqUploadTestFiles(data=request.data)
    if not inSerializer.is_valid():
        message = f"Verification failed in {testPreview.cls.__name__}"
        exception = f"Verification failed {inSerializer.errors}"
        loggerError.error(message)
        exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
        if exceptionSerializer.is_valid():
            return Response(exceptionSerializer.data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    zipFile = BytesIO()
    with zipfile.ZipFile(zipFile, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        with tempfile.TemporaryDirectory() as tempDir: # because get_jpeg_preview does not accept BytesIO, we have to use this bs
            manager = PreviewManager(tempDir+"/previews", create_folder= True)
            fileNames = list(request.FILES.keys())
            for fileName in fileNames:
                for file in request.FILES.getlist(fileName):
                    temporaryFileName = tempDir+"/"+file.name
                    temporaryFile = open(temporaryFileName, 'wb')
                    temporaryFile.write(file.read())
                    temporaryFile.close()
                    fileNameRoot, extension= os.path.splitext(file.name)
                    #print(file.name, fileNameRoot, extension)
                    #fileContent = file.read()
                    try:
                        path_to_preview_image = manager.get_jpeg_preview(temporaryFileName)
                        f = open(path_to_preview_image, 'rb')
                        zf.writestr(fileNameRoot+".jpg", f.read())
                        f.close()
                        #outStr = stlToBinJpg(file)
                    except UnsupportedMimeType as unsupported:
                        loggerError.error(f"Unsupported file type: {str(unsupported)}")
                        continue
                    except Exception as error:
                        loggerError.error(f"Error while creating preview: {str(error)}")
                        continue
    zipFile.seek(0)
    fileResponse = FileResponse(zipFile, as_attachment=True, filename="files.zip")
    #fileResponse = createFileResponse(zipFile, filename="files.zip")
    fileResponse["Content-Disposition"] = 'attachment; filename="files.zip"'.format("files.zip")
    return fileResponse