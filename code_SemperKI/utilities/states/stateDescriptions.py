"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Contains the state machine and fellow classes
"""

import enum
from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactylAsDefined



###############################################################################
# Definitions
#######################################################
class ProcessStatusAsString(StrEnumExactylAsDefined):
    """
    Defines all statuus for the process (independent of the selected service)
    """
    DRAFT = enum.auto()
    WAITING_FOR_OTHER_PROCESS = enum.auto()
    SERVICE_READY = enum.auto()
    SERVICE_IN_PROGRESS = enum.auto()
    SERVICE_COMPLICATION = enum.auto()
    CONTRACTOR_SELECTED = enum.auto()
    VERIFYING = enum.auto()
    VERIFIED = enum.auto()
    REQUESTED = enum.auto()
    CLARIFICATION = enum.auto()
    CONFIRMED_BY_CONTRACTOR = enum.auto()
    REJECTED_BY_CONTRACTOR = enum.auto()
    CONFIRMED_BY_CLIENT = enum.auto()
    REJECTED_BY_CLIENT = enum.auto()
    PRODUCTION = enum.auto()
    DELIVERY = enum.auto()
    DISPUTE = enum.auto()
    COMPLETED = enum.auto()
    FAILED = enum.auto()
    CANCELED = enum.auto()

###################################################
# Statuscodes
def processStatusAsInt(statusString:str) -> int:
    """
    Defines all statuus for the process as an integer
    """
    if statusString == ProcessStatusAsString.DRAFT:
        return 0
    elif statusString == ProcessStatusAsString.WAITING_FOR_OTHER_PROCESS:
        return 100
    elif statusString == ProcessStatusAsString.SERVICE_READY:
        return 200
    elif statusString == ProcessStatusAsString.SERVICE_IN_PROGRESS:
        return 201
    elif statusString == ProcessStatusAsString.SERVICE_COMPLICATION:
        return 202
    elif statusString == ProcessStatusAsString.CONTRACTOR_SELECTED:
        return 300
    elif statusString == ProcessStatusAsString.VERIFYING:
        return 400
    elif statusString == ProcessStatusAsString.VERIFIED:
        return 500
    elif statusString == ProcessStatusAsString.REQUESTED:
        return 600
    elif statusString == ProcessStatusAsString.CLARIFICATION:
        return 700
    elif statusString == ProcessStatusAsString.CONFIRMED_BY_CONTRACTOR:
        return 800
    elif statusString == ProcessStatusAsString.REJECTED_BY_CONTRACTOR:
        return 801
    elif statusString == ProcessStatusAsString.CONFIRMED_BY_CLIENT:
        return 900
    elif statusString == ProcessStatusAsString.REJECTED_BY_CLIENT:
        return 901
    elif statusString == ProcessStatusAsString.PRODUCTION:
        return 1000
    elif statusString == ProcessStatusAsString.DELIVERY:
        return 1100
    elif statusString == ProcessStatusAsString.DISPUTE:
        return 1200
    elif statusString == ProcessStatusAsString.COMPLETED:
        return 1300
    elif statusString == ProcessStatusAsString.FAILED:
        return 1400
    elif statusString == ProcessStatusAsString.CANCELED:
        return 1500
    else:
        return 0

###################################################
def processStatusFromIntToStr(statusCode:int) -> str:
    """
    Interprets the integer back to the string code
    """ 
    if statusCode == 0:
        return ProcessStatusAsString.DRAFT
    elif statusCode == 100:
        return ProcessStatusAsString.WAITING_FOR_OTHER_PROCESS
    elif statusCode == 200:
        return ProcessStatusAsString.SERVICE_READY
    elif statusCode == 201:
        return ProcessStatusAsString.SERVICE_IN_PROGRESS
    elif statusCode == 202:
        return ProcessStatusAsString.SERVICE_COMPLICATION
    elif statusCode == 300:
        return ProcessStatusAsString.CONTRACTOR_SELECTED
    elif statusCode == 400:
        return ProcessStatusAsString.VERIFYING
    elif statusCode == 500:
        return ProcessStatusAsString.VERIFIED
    elif statusCode == 600:
        return ProcessStatusAsString.REQUESTED
    elif statusCode == 700:
        return ProcessStatusAsString.CLARIFICATION
    elif statusCode == 800:
        return ProcessStatusAsString.CONFIRMED_BY_CONTRACTOR
    elif statusCode == 801:
        return ProcessStatusAsString.REJECTED_BY_CONTRACTOR
    elif statusCode == 900:
        return ProcessStatusAsString.CONFIRMED_BY_CLIENT
    elif statusCode == 901:
        return ProcessStatusAsString.REJECTED_BY_CLIENT
    elif statusCode == 1000:
        return ProcessStatusAsString.PRODUCTION
    elif statusCode == 1100:
        return ProcessStatusAsString.DELIVERY
    elif statusCode == 1200:
        return ProcessStatusAsString.DISPUTE
    elif statusCode == 1300:
        return ProcessStatusAsString.COMPLETED
    elif statusCode == 1400:
        return ProcessStatusAsString.FAILED
    elif statusCode == 1500:
        return ProcessStatusAsString.CANCELED
    else:
        return ProcessStatusAsString.DRAFT


#######################################################
class InterfaceForStateChange(StrEnumExactylAsDefined):
    """
    What does the json consist of that is sent back and forth?

    """

    projectID = enum.auto()
    processIDs = enum.auto()
    buttonData = enum.auto()
    targetStatus = enum.auto()
    CLICKED_BUTTON = enum.auto()

#######################################################
class ButtonLabels(StrEnumExactylAsDefined):
    """
    So that the frontend can render it correctly. 
    Do not edit unless you change it in the translation file of the frontend as well!

    """
    BACK = enum.auto()
    SELECT_SERVICE = enum.auto()
    EDIT = enum.auto()
    DELETE = enum.auto()
    CONTRACTOR_SELECTED = enum.auto()
    VERIFYING_AND_REQUESTED = enum.auto()
    VERIFYING = enum.auto()
    REQUESTED = enum.auto()
    CLARIFICATION = enum.auto()
    CONFIRMED_BY_CONTRACTOR = enum.auto()
    REJECTED_BY_CONTRACTOR = enum.auto()
    CONFIRMED_BY_CLIENT = enum.auto()
    REJECTED_BY_CLIENT = enum.auto()
    PRODUCTION = enum.auto()
    DELIVERY = enum.auto()
    COMPLETED = enum.auto()
    REPROJECT = enum.auto()
    SERVICE_IN_PROGRESS = enum.auto()
    NONE = enum.auto()

#######################################################
class ButtonTypes(StrEnumExactylAsDefined):
    """
    Types of buttons
    
    """
    primary = enum.auto()
    secondary = enum.auto()

#######################################################
class IconType(StrEnumExactylAsDefined):
    """
    Names for the specific icons
    
    """
    ArrowBackIcon = enum.auto()
    DeleteIcon = enum.auto()
    FactoryIcon = enum.auto()
    TroubleshootIcon = enum.auto()
    ScheduleSendIcon = enum.auto()
    MailIcon = enum.auto()
    QuestionAnswerIcon = enum.auto()
    DescriptionIcon = enum.auto()
    CancelIcon = enum.auto()
    DoneAllIcon = enum.auto()
    LocalShippingIcon = enum.auto()
    TaskIcon = enum.auto()
    ReplayIcon = enum.auto()

