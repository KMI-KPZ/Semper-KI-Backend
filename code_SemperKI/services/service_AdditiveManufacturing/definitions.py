"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""

import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactylAsDefined

##################################################
# What makes up the 3D print service
class ServiceDetails(StrEnumExactylAsDefined):
    """
    What does the service consists of 

    """
    models = enum.auto()
    materials = enum.auto()
    postProcessings = enum.auto()
    calculations = enum.auto()

##################################################
# What defines a material?
class MaterialDetails(StrEnumExactylAsDefined):
    """
    What does a material entry contain?
    """
    id = enum.auto()
    title = enum.auto()
    propList = enum.auto()
    imgPath = enum.auto()


##################################################
# What defines a material?
class PostProcessDetails(StrEnumExactylAsDefined):
    """
    What does a postprocess entry contain?
    """
    id = enum.auto()
    title = enum.auto()
    checked = enum.auto()
    selectedValue = enum.auto()
    valueList = enum.auto()
    type = enum.auto()
    imgPath = enum.auto()



# TODO: Service Status Codes