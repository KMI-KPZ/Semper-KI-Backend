"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""
import enum

###################################################
from .modelFiles.processModel import ProcessDescription
from .modelFiles.projectModel import ProjectDescription

###################################################
# Statuscodes
class ProcessStatus(enum.Enum):
    """
    Defines all statuus for the process (independent of the selected service)
    """
    DRAFT = 0
    WAITING_FOR_OTHER_PROCESS =  100
    SERVICE_READY =  200
    SERVICE_IN_PROGRESS =  201
    SERVICE_COMPLICATION =  202
    CONTRACTOR_SELECTED =  300
    VERIFYING =  400
    VERIFIED =  500
    REQUESTED =  600
    CLARIFICATION =  700
    CONFIRMED_BY_CONTRACTOR =  800
    REJECTED_BY_CONTRACTOR =  801
    CONFIRMED_BY_CLIENT =  900
    REJECTED_BY_CLIENT =  901
    PRODUCTION =  1000
    DELIVERY =  1100
    DISPUTE =  1200
    COMPLETED =  1300
    FAILED =  1400
    CANCELED =  1500



###################################################
# Data Types
class DataType(enum.Enum):
    """
    Defines the types of data that are saved in the database of the same name
    
    """
    STATUS = 1
    MESSAGE = 2
    FILE = 3
    DELETION = 4

####################################################################################
# Enum for updateProcess
class ProcessUpdates(enum.Enum):
    """
    What types of updates are there for a process? 
    
    """
    STATUS = 1
    MESSAGES = 2
    FILES = 3
    SERVICE = 4
    SERVICE_TYPE = 5
    CONTRACTOR = 6
    DETAILS = 7

####################################################################################
# Enum for processDetails
class ProcessDetails(enum.StrEnum):
    """
    What Details can a Process have?
    
    """
    NAME = enum.auto()
    PROVISIONAL_CONTRACTOR = enum.auto()

####################################################################################
# Enum for session content
class SessionContentSemperKI(enum.StrEnum):
    """
    Name of all added keys to the session for uniform naming
    
    """
    CURRENT_PROJECTS = enum.auto()
