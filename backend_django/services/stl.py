import io, time
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot
import numpy as np
from PIL import Image
import base64

#######################################################
def stlToJpg(file):
    """
    Convert stl file to jpg

    :param request: open file from redis
    :type request: binary string
    :return: jpg for rendering
    :rtype: JPG as binary string

    """
    # Create a new plot
    figure = pyplot.figure(figsize=(4,4), dpi=100)
    axes = figure.add_subplot(projection='3d')

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
    img.save(convertedJpg, format="jpeg", bbox_inches='tight')
    return convertedJpg.getvalue()

#######################################################
def binToJpg(binaryString):
    """
    Convert binary string to jpg

    :param binaryString: binary string
    :type request: string

    """
    decoded = base64.b64decode(binaryString)
    img = Image.open(io.BytesIO(decoded))
    img.save("test2.jpg")
        