"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""

##################################################
# What makes up the Assembly service
import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

##################################################
# Service specific definitions
SERVICE_NAME = "ASSEMBLY"
SERVICE_NUMBER = 8

###################################################
class ServiceDetails(StrEnumExactlyAsDefined):
    """
    What does the service consists of 

    """

####################################################
class NodeTypesA(StrEnumExactlyAsDefined):
    """
    What possible types can a node have in the AS service?
    
    """
    organization = enum.auto() # the orga node

##################################################
class OrganizationDetailsA(StrEnumExactlyAsDefined):
    """
    What are the details of an organization?
    
    """

##################################################