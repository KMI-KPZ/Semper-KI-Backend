"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""
import enum
from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactylAsDefined

###################################################
# Version of the backend
SEMPER_KI_VERSION = "0.2.1"

###################################################
from .modelFiles.processModel import ProcessDescription
from .modelFiles.projectModel import ProjectDescription
from .modelFiles.dataModel import DataDescription

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
    SERVICE = 8
    DEPENDENCY = 9

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
    elif dataType == DataType.SERVICE:
        return "SERVICE"
    elif dataType == DataType.DEPENDENCY:
        return "DEPENDENCY"
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
    dependenciesIn = enum.auto()
    dependenciesOut = enum.auto()

####################################################################################
# Enum for processDetails
class ProjectDetails(StrEnumExactylAsDefined):
    """
    What Details can a Project have?
    
    """
    title = enum.auto()

####################################################################################
# Enum for processDetails
class ProcessDetails(StrEnumExactylAsDefined):
    """
    What Details can a Process have?
    
    """
    provisionalContractor = enum.auto()
    amount = enum.auto()
    title = enum.auto()
    clientBillingAddress = enum.auto()
    clientDeliverAddress = enum.auto()
    imagePath = enum.auto()


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
#Enum for MessageOrigin
class MessageInterfaceFromFrontend(StrEnumExactylAsDefined):
    """
    What does a message origin consist of?
    
    """
    messages = enum.auto()
    origin = enum.auto()
    
####################################################################################
# Enum for session content
class SessionContentSemperKI(StrEnumExactylAsDefined):
    """
    Name of all added keys to the session for uniform naming
    
    """
    CURRENT_PROJECTS = enum.auto()
    processes = enum.auto()

####################################################################################
# Enum for events
class EventsDescription(StrEnumExactylAsDefined):
    """
    Websocket events and missed events should be in the same format

    """
    eventType = enum.auto()
    events = enum.auto()
    projectEvent = enum.auto()
    orgaEvent = enum.auto()
    
####################################################################################
# Enum for flat process status
class FlatProcessStatus(StrEnumExactylAsDefined):
    """
    For Frontend
    
    """
    ACTION_REQUIRED = enum.auto()
    WAITING_CONTRACTOR= enum.auto()
    WAITING_CLIENT = enum.auto()
    WAITING_PROCESS = enum.auto()
    IN_PROGRESS = enum.auto()
    COMPLETED = enum.auto()