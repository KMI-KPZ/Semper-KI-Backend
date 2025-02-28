"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""

##################################################
# What makes up the Quality Control service
import enum

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

##################################################
# Service specific definitions
SERVICE_NAME = "QUALITY_CONTROL"
SERVICE_NUMBER = 6

###################################################
class ServiceDetails(StrEnumExactlyAsDefined):
    """
    What does the service consists of 

    """

####################################################
class NodeTypesQC(StrEnumExactlyAsDefined):
    """
    What possible types can a node have in the QC service?
    
    """
    organization = enum.auto() # the orga node

##################################################
class OrganizationDetailsQC(StrEnumExactlyAsDefined):
    """
    What are the details of an organization?
    
    """

##################################################