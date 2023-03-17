import numpy, io
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot

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
    figure = pyplot.figure()
    axes = figure.add_subplot(projection='3d')

    # Load the STL files and add the vectors to the plot
    #tempFile = file.read()
    your_mesh = mesh.Mesh.from_file("",fh=file)
    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))

    # Auto scale to the mesh size
    scale = your_mesh.points.flatten()
    axes.auto_scale_xyz(scale, scale, scale)

    # Save file into binary string
    convertedJpg = io.BytesIO()
    pyplot.savefig(convertedJpg, format="jpg")
    return convertedJpg.getvalue()