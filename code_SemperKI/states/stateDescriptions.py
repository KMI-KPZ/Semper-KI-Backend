"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Contains definitions for the state machine
"""

import enum
from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined



###############################################################################
# Definitions
#######################################################
class ProcessStatusAsString(StrEnumExactlyAsDefined):
    """
    Defines all statuus for the process (independent of the selected service)
    """
    DRAFT = enum.auto(), #kein Service Ausgewählt
    WAITING_FOR_OTHER_PROCESS = enum.auto(), #warten auf anderen Prozess
    SERVICE_READY = enum.auto(), #Service bereit
    SERVICE_IN_PROGRESS = enum.auto(), #Service in Bearbeitung
    SERVICE_COMPLICATION = enum.auto(), #Service Komplikation
    SERVICE_COMPLETED = enum.auto(), #Service abgeschlossen
    CONTRACTOR_COMPLETED = enum.auto(), #auftragnehmer ausgewählt
    VERIFYING = enum.auto(), #verifizierung in bearbeitung
    VERIFICATION_COMPLETED = enum.auto(), #verifizierung abgeschlossen
    REQUEST_COMPLETED = enum.auto(), #auftrag raus
    OFFER_COMPLETED = enum.auto(), #angebot raus
    OFFER_REJECTED = enum.auto(), #angebot abgelehnt
    CONFIRMATION_COMPLETED = enum.auto(), #bestätigung raus
    CONFIRMATION_REJECTED = enum.auto(), #bestätigung abgelehnt
    PRODUCTION_IN_PROGRESS = enum.auto(), #produktion in bearbeitung
    PRODUCTION_COMPLETED = enum.auto(), #produktion abgeschlossen
    DELIVERY_IN_PROGRESS = enum.auto(), #lieferung in bearbeitung
    DELIVERY_COMPLETED = enum.auto(), #lieferung abgeschlossen
    DISPUTE = enum.auto(), #streitfall
    COMPLETED = enum.auto(), #abgeschlossen
    FAILED = enum.auto(), #fehlgeschlagen
    CANCELED = enum.auto(), #abgebrochen
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
    elif statusString == ProcessStatusAsString.SERVICE_COMPLETED:
        return 203
    elif statusString == ProcessStatusAsString.CONTRACTOR_COMPLETED:
        return 300
    elif statusString == ProcessStatusAsString.VERIFYING:
        return 400
    elif statusString == ProcessStatusAsString.VERIFICATION_COMPLETED:
        return 401
    elif statusString == ProcessStatusAsString.REQUEST_COMPLETED:
        return 500
    elif statusString == ProcessStatusAsString.OFFER_COMPLETED:
        return 600
    elif statusString == ProcessStatusAsString.OFFER_REJECTED:
        return 601
    elif statusString == ProcessStatusAsString.CONFIRMATION_COMPLETED:
        return 700
    elif statusString == ProcessStatusAsString.CONFIRMATION_REJECTED:
        return 701
    elif statusString == ProcessStatusAsString.PRODUCTION_IN_PROGRESS:
        return 800
    elif statusString == ProcessStatusAsString.PRODUCTION_COMPLETED:
        return 801
    elif statusString == ProcessStatusAsString.DELIVERY_IN_PROGRESS:
        return 900
    elif statusString == ProcessStatusAsString.DELIVERY_COMPLETED:
        return 901
    elif statusString == ProcessStatusAsString.DISPUTE:
        return 1000
    elif statusString == ProcessStatusAsString.COMPLETED:
        return 1100
    elif statusString == ProcessStatusAsString.FAILED:
        return 1200
    elif statusString == ProcessStatusAsString.CANCELED:
        return 1300
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
    elif statusCode == 203:
        return ProcessStatusAsString.SERVICE_COMPLETED
    elif statusCode == 300:
        return ProcessStatusAsString.CONTRACTOR_COMPLETED
    elif statusCode == 400:
        return ProcessStatusAsString.VERIFYING
    elif statusCode == 401:
        return ProcessStatusAsString.VERIFICATION_COMPLETED
    elif statusCode == 500:
        return ProcessStatusAsString.REQUEST_COMPLETED
    elif statusCode == 600:
        return ProcessStatusAsString.OFFER_COMPLETED
    elif statusCode == 601:
        return ProcessStatusAsString.OFFER_REJECTED
    elif statusCode == 700:
        return ProcessStatusAsString.CONFIRMATION_COMPLETED
    elif statusCode == 701:
        return ProcessStatusAsString.CONFIRMATION_REJECTED
    elif statusCode == 800:
        return ProcessStatusAsString.PRODUCTION_IN_PROGRESS
    elif statusCode == 801:
        return ProcessStatusAsString.PRODUCTION_COMPLETED
    elif statusCode == 900:
        return ProcessStatusAsString.DELIVERY_IN_PROGRESS
    elif statusCode == 901:
        return ProcessStatusAsString.DELIVERY_COMPLETED
    elif statusCode == 1000:
        return ProcessStatusAsString.DISPUTE
    elif statusCode == 1100:
        return ProcessStatusAsString.COMPLETED
    elif statusCode == 1200:
        return ProcessStatusAsString.FAILED
    elif statusCode == 1300:
        return ProcessStatusAsString.CANCELED
    else:
        return ProcessStatusAsString.DRAFT


#######################################################
class InterfaceForStateChange(StrEnumExactlyAsDefined):
    """
    What does the json consist of that is sent back and forth?

    """

    projectID = enum.auto()
    processIDs = enum.auto()
    buttonData = enum.auto()
    targetStatus = enum.auto()
    CLICKED_BUTTON = enum.auto()
    type = enum.auto()

#######################################################
class ButtonLabels(StrEnumExactlyAsDefined):
    """
    So that the frontend can render it correctly. 
    Do not edit unless you change it in the translation file of the frontend as well!

    """
    BACK = enum.auto()
    FORWARD = enum.auto()
    SELECT_SERVICE = enum.auto()
    SERVICE_COMPLICATION = enum.auto() # TODO not in frontend currently
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
    DISPUTE = enum.auto() #TODO not in frontend currently
    SERVICE_IN_PROGRESS = enum.auto()
    FAILED = enum.auto() #TODO not in frontend currently
    NONE = enum.auto()
    CLONE = enum.auto() # TODO not in frontend currently

#######################################################
class ButtonTypes(StrEnumExactlyAsDefined):
    """
    Types of buttons
    
    """
    primary = enum.auto()
    secondary = enum.auto()

#######################################################
class IconType(StrEnumExactlyAsDefined):
    """
    Names for the specific icons
    
    """
    ArrowBackIcon = enum.auto()
    ArrowForwardIcon = enum.auto()
    DeleteIcon = enum.auto()
    FactoryIcon = enum.auto()
    TroubleshootIcon = enum.auto()
    ScheduleSendIcon = enum.auto()
    MailIcon = enum.auto()
    QuestionAnswerIcon = enum.auto()
    DescriptionIcon = enum.auto()
    CancelIcon = enum.auto()
    DoneAllIcon = enum.auto()
    DoneIcon = enum.auto()
    LocalShippingIcon = enum.auto()
    TaskIcon = enum.auto()
    ReplayIcon = enum.auto()
    CloneIcon = enum.auto() 

