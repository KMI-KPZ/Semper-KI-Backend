"""
Part of Semper-KI software

Silvio Weging 2023
Lukas Hein 2024

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""

##################################################
# What makes up the Packaging service
import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

##################################################
# Service specific definitions
SERVICE_NAME = "PACKAGING"
SERVICE_NUMBER = 5

###################################################
class ServiceDetails(StrEnumExactlyAsDefined):
    """
    What does the service consists of 

    """

####################################################
class NodeTypesP(StrEnumExactlyAsDefined):
    """
    What possible types can a node have in the A service?
    
    """
    organization = enum.auto() # the orga node

##################################################
class OrganizationDetailsP(StrEnumExactlyAsDefined):
    """
    What are the details of an organization?
    
    """

##################################################