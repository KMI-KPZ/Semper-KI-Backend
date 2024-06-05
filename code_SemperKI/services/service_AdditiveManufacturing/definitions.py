"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""

##################################################
# What makes up the 3D print service
import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactylAsDefined

class ServiceDetails(StrEnumExactylAsDefined):
    """
    What does the service consists of 

    """
    models = enum.auto()
    materials = enum.auto()
    postProcessings = enum.auto()
    calculations = enum.auto()

# TODO: Service Status Codes