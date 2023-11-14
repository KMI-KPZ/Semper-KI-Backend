"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for generating a preview of stl files
"""

import io, time
from stl import mesh
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot
import numpy as np
from PIL import Image
import base64
from logging import getLogger

logger = getLogger("django")


# def find_mins_maxs(obj):
#     minx = obj.x.min()
#     maxx = obj.x.max()
#     miny = obj.y.min()
#     maxy = obj.y.max()
#     minz = obj.z.min()
#     maxz = obj.z.max()
#     return minx, maxx, miny, maxy, minz, maxz

#######################################################
async def stlToBinJpg(file) -> str:
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
        logger.error(f"Error while converting stl to jpg: {str(error)}")
        return base64.b64encode(error)

#######################################################
def binToJpg(binaryString):
    """
    Convert binary string to jpg

    :param binaryString: binary string
    :type request: string

    """
    decoded = base64.b64decode(binaryString)
    img = Image.open(io.BytesIO(decoded))
    img.save("test.jpg")
        