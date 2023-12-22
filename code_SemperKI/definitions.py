"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""
import enum
from code_General.utilities.customStrEnum import StrEnumExactylAsDefined

###################################################
from .modelFiles.processModel import ProcessDescription
from .modelFiles.projectModel import ProjectDescription
from .modelFiles.dataModel import DataDescription

###################################################
# Statuscodes
class ProcessStatus(enum.IntEnum):
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
class DataType(enum.IntEnum):
    """
    Defines the types of data that are saved in the database of the same name
    
    """
    CREATION = 1
    STATUS = 2
    MESSAGE = 3
    FILE = 4
    DELETION = 5
    DETAILS = 6
    OTHER = 7

####################################################################################
def dataTypeToString(dataType:DataType):
    """
    Convert integer to string
    
    """

    if dataType == DataType.CREATION:
        return "CREATION"
    elif dataType == DataType.STATUS:
        return "STATUS"
    elif dataType == DataType.MESSAGE:
        return "MESSAGE"
    elif dataType == DataType.FILE:
        return "FILE"
    elif dataType == DataType.DELETION:
        return "DELETION"
    elif dataType == DataType.DETAILS:
        return "DETAILS"
    elif dataType == DataType.OTHER:
        return "OTHER"
    return ""

####################################################################################
# Enum for updateProcess
class ProjectUpdates(StrEnumExactylAsDefined):
    """
    What types of updates are there for a project?

    """
    projectStatus = enum.auto()
    projectDetails = enum.auto()

####################################################################################
# Enum for updateProcess
class ProcessUpdates(StrEnumExactylAsDefined):
    """
    What types of updates are there for a process? 
    
    """
    messages = enum.auto()
    files = enum.auto()
    serviceDetails = enum.auto()
    serviceType = enum.auto()
    serviceStatus = enum.auto()
    processDetails = enum.auto()
    processStatus = enum.auto()
    provisionalContractor = enum.auto()

####################################################################################
# Enum for processDetails
class ProcessDetails(StrEnumExactylAsDefined):
    """
    What Details can a Process have?
    
    """
    name = enum.auto()
    provisionalContractor = enum.auto()

####################################################################################
# Enum for messages
class MessageContent(StrEnumExactylAsDefined):
    """
    What does a message consists of?
    
    """
    date = enum.auto()
    userID = enum.auto()
    userName = enum.auto()
    text = enum.auto()

####################################################################################
# Enum for session content
class SessionContentSemperKI(StrEnumExactylAsDefined):
    """
    Name of all added keys to the session for uniform naming
    
    """
    CURRENT_PROJECTS = enum.auto()
    processes = enum.auto()