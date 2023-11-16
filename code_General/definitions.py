"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""
import enum

###################################################
# Services
class ServiceType(enum.Enum):
    ADDITIVE_MANUFACTURING = 1,
    CREATE_3D_MODEL = 2