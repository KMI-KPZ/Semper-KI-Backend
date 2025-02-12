"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""

##################################################
# What makes up the Create Model service
import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

##################################################
# Service specific definitions
SERVICE_NAME = "CREATE_MODEL"
SERVICE_NUMBER = 2

###################################################
class ServiceDetails(StrEnumExactlyAsDefined):
    """
    What does the service consists of 

    """

####################################################
class NodeTypesCM(StrEnumExactlyAsDefined):
    """
    What possible types can a node have in the CM service?
    
    """
    organization = enum.auto() # the orga node

##################################################
class OrganizationDetailsCM(StrEnumExactlyAsDefined):
    """
    What are the details of an organization?
    
    """

##################################################