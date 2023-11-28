"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""

##################################################
# What makes up the 3D print service
import enum

from code_General.utilities.customStrEnum import StrEnumExactylAsDefined

class ServiceDetails(StrEnumExactylAsDefined):
    """
    What does the service consists of 

    """
    model = enum.auto()
    material = enum.auto()
    postProcessings = enum.auto()