"""
Part of Semper-KI software

Silvio Weging 2023
Lukas Hein 2024

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""

##################################################
# What makes up the Post Processing service
import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

##################################################
# Service specific definitions
SERVICE_NAME = "POST_PROCESSING"
SERVICE_NUMBER = 4

###################################################
class ServiceDetails(StrEnumExactlyAsDefined):
    """
    What does the service consists of 

    """

####################################################
class NodeTypesPP(StrEnumExactlyAsDefined):
    """
    What possible types can a node have in the PP service?
    
    """
    organization = enum.auto() # the orga node

##################################################
class OrganizationDetailsPP(StrEnumExactlyAsDefined):
    """
    What are the details of an organization?
    
    """

##################################################