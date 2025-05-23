"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services

"""
import enum
from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

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
class ProjectUpdates(StrEnumExactlyAsDefined):
    """
    What types of updates are there for a project?

    """
    projectStatus = enum.auto()
    projectDetails = enum.auto()

####################################################################################
# Enum for updateProcess
class ProcessUpdates(StrEnumExactlyAsDefined):
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
    verificationResults = enum.auto()
    additionalInput = enum.auto()

####################################################################################
# Enum for processDetails
class ProjectDetails(StrEnumExactlyAsDefined):
    """
    What Details can a Project have?
    
    """
    title = enum.auto()

####################################################################################
# Enum for processDetails
class ProcessDetails(StrEnumExactlyAsDefined):
    """
    What Details can a Process have?
    
    """
    provisionalContractor = enum.auto()
    title = enum.auto()
    clientBillingAddress = enum.auto()
    clientDeliverAddress = enum.auto()
    imagePath = enum.auto()
    priorities = enum.auto()
    prices = enum.auto()
    verificationResults = enum.auto()
    additionalInput = enum.auto()

####################################################################################
# Enum for the output of the process
class ProcessOutput(StrEnumExactlyAsDefined):
    """
    What should the output object contain?
    
    """
    processStatusButtons = enum.auto()
    processErrors = enum.auto()
    flatProcessStatus = enum.auto()

####################################################################################
# Enum for the output of the project
class ProjectOutput(StrEnumExactlyAsDefined):
    owner = enum.auto()
    processIDs = enum.auto()
    searchableData = enum.auto()
    processesCount = enum.auto()


####################################################################################
# Enum for prices
class PricesDetails(StrEnumExactlyAsDefined):
    """
    What should the prices object contain?
    
    """
    details = enum.auto()

####################################################################################
# Enum for messages
class MessageContent(StrEnumExactlyAsDefined):
    """
    What does a message consists of?
    
    """
    date = enum.auto()
    userID = enum.auto()
    userName = enum.auto()
    text = enum.auto()

####################################################################################
#Enum for MessageOrigin
class MessageInterfaceFromFrontend(StrEnumExactlyAsDefined):
    """
    What does a message origin consist of?
    
    """
    messages = enum.auto()
    origin = enum.auto()
    date = enum.auto()
    text = enum.auto()
    userID = enum.auto()
    userName = enum.auto()
    createdBy = enum.auto()
    
####################################################################################
# Enum for session content
class SessionContentSemperKI(StrEnumExactlyAsDefined):
    """
    Name of all added keys to the session for uniform naming
    
    """
    CURRENT_PROJECTS = enum.auto()
    processes = enum.auto()

    
####################################################################################
# Enum for flat process status
class FlatProcessStatus(StrEnumExactlyAsDefined):
    """
    For Frontend
    
    """
    ACTION_REQUIRED = enum.auto()
    WAITING_CONTRACTOR= enum.auto()
    WAITING_CLIENT = enum.auto()
    WAITING_PROCESS = enum.auto()
    IN_PROGRESS = enum.auto()
    FAILED = enum.auto()
    COMPLETED = enum.auto()

####################################################################################
# Enum for organization details for SemperKI
class OrganizationDetailsSKI(StrEnumExactlyAsDefined):
    maturityLevel = enum.auto()
    resilienceScore = enum.auto()
    todos = enum.auto()

####################################################################################
# Enum for user details for SemperKI
class UserDetailsSKI(StrEnumExactlyAsDefined):
    todos = enum.auto()

####################################################################################
# Enum for Addresses for SemperKI
class AddressesSKI(StrEnumExactlyAsDefined):
    """
    What address-specific fields are there for SKI?
    """
    coordinates = enum.auto()

####################################################################################
# Enum for notification settings
class NotificationSettingsUserSemperKI(StrEnumExactlyAsDefined):
    """
    Which notifications exist for users?
    
    """
    verification = enum.auto()
    processSent = enum.auto()
    responseFromContractor = enum.auto()
    statusChange = enum.auto()
    newMessage = enum.auto()
    actionReminder = enum.auto()
    errorOccurred = enum.auto()

####################################################################################
# Enum for notification settings
class NotificationSettingsOrgaSemperKI(StrEnumExactlyAsDefined):
    """
    Which notifications exist for orgas?
    
    """
    processReceived = enum.auto()
    responseFromClient = enum.auto()
    statusChange = enum.auto()
    newMessage = enum.auto()
    actionReminder = enum.auto()
    errorOccurred = enum.auto()

###################################################
# Enum for priorities for orgas
class PrioritiesForOrganizationSemperKI(StrEnumExactlyAsDefined):
    """
    If the organization has some priorities, they can be set here
    Is used for calculations
    """
    cost = enum.auto()
    time = enum.auto()
    quality = enum.auto()
    quantity = enum.auto()
    resilience = enum.auto()
    sustainability = enum.auto()

##################################################
# Enum for values of priorities
class PriorityTargetsSemperKI(StrEnumExactlyAsDefined):
    """
    What does every priority contain
    
    """
    value = enum.auto() # the integer value

##################################################
# Permission enum
class PermissionsEnum(enum.StrEnum):
    """
    What permissions are there?
    
    """
    proccessesRead = "processes:read"
    processesFiles = "processes:files"
    processesMessages = "processes:messages"
    processesEdit = "processes:edit"
    processesDelete = "processes:delete"
    orgaEdit = "orga:edit"
    orgaDelete = "orga:delete"
    orgaRead = "orga:read"
    resourcesRead = "resources:read"
    resourcesEdit = "resources:edit"

##################################################
# Class that contains a dictionary which maps the permissions to the notifications
class MapPermissionsToOrgaNotifications():
    """
    Contains a dictionary which maps the permissions to the notifications
    """
    permissionsToNotifications = {
        # all: [x.value for x in NotificationSettingsOrgaSemperKI]
        PermissionsEnum.proccessesRead: [NotificationSettingsOrgaSemperKI.processReceived.value, NotificationSettingsOrgaSemperKI.responseFromClient.value, NotificationSettingsOrgaSemperKI.statusChange.value, NotificationSettingsUserSemperKI.verification.value, NotificationSettingsUserSemperKI.processSent.value, NotificationSettingsUserSemperKI.responseFromContractor.value], 
        PermissionsEnum.processesFiles: [], 
        PermissionsEnum.processesMessages: [NotificationSettingsOrgaSemperKI.newMessage.value], 
        PermissionsEnum.processesEdit : [NotificationSettingsOrgaSemperKI.actionReminder.value, NotificationSettingsOrgaSemperKI.errorOccurred.value], 
        PermissionsEnum.processesDelete: [], 
        PermissionsEnum.orgaEdit: [],
        PermissionsEnum.orgaDelete: [],
        PermissionsEnum.orgaRead: [],
        PermissionsEnum.resourcesRead: [], 
        PermissionsEnum.resourcesEdit: [],	
    }

##################################################
# Class that contains the structure of service specific fields for organization details
class ServiceSpecificFields(StrEnumExactlyAsDefined):
    """
    Contains the structure of service specific fields for organization details
    """
    key = enum.auto()
    name = enum.auto()
    unit = enum.auto()
    value = enum.auto()

##################################################
# Class that contains all units used for price calculation
class UnitsForPriceCalculation(enum.StrEnum):
    """
    Contains all units used for price calculation
    """
    euroPerkWh = "€/kWh"
    euroPerHour = "€/h"
    percent = "%"
    euroPerKilogram = "€/kg"
    euro = "€"
    cubicCentimeterPerHour = "cm³/h"
    millimeter = "mm"
    cubicCentimeter = "cm³"
    grammPerCubicCentimeter = "g/cm³"
    euroPerHourPerSquareMeter = "€/(h*m²)"
    
##################################################
class ValidationSteps(StrEnumExactlyAsDefined):
    """
    The steps of the validation process
    """
    serviceReady = enum.auto()
    serviceSpecificTasks = enum.auto()

##################################################
class ValidationInformationForFrontend(StrEnumExactlyAsDefined):
    """
    What is the content of the verification stuff that the frontend needs
    
    """
    isSuccessful = enum.auto()
    reason = enum.auto()

##################################################
class ContractorParsingForFrontend(StrEnumExactlyAsDefined):
    """
    How the frontend wants the output of the contractors
    
    """
    contractors = enum.auto()
    errors = enum.auto()
    groupID = enum.auto()
    error = enum.auto()