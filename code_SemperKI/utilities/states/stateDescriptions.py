"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Contains the state machine and fellow classes
"""

import enum

from abc import ABC, abstractmethod

import code_SemperKI.connections.content.session as SessionInterface
import code_SemperKI.connections.content.postgresql.pgProcesses as DBInterface
import code_SemperKI.modelFiles.processModel as ProcessModel
import code_SemperKI.utilities.states.states as states

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactylAsDefined
from ...definitions import SessionContentSemperKI, ProcessDescription


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

    processIDs = enum.auto()
    CURRENT_STATE = enum.auto()
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

###############################################################################
# Functions
#######################################################
def addButtonsToProcess(projectObj) -> None: #is changed in place
    """
    Look at process status of every process of a project and add respective buttons
    """
    for process in projectObj[SessionContentSemperKI.processes]:
        processStatusAsString = processStatusFromIntToStr(process[ProcessDescription.processStatus])
        process["processStatusButtons"] = returnCorrectState(processStatusAsString).buttons()


#######################################################
# TODO solve this better by creating a global dictionary or a static class or something
def returnCorrectState(stateString:str):
    """
    Return the state class with respect to the string provided

    :param stateString: Contains the string with respect to the enum
    :type stateString: str
    :return: Subclass object of the State class
    :rtype: State()
    
    """

    if stateString == ProcessStatusAsString.DRAFT:
        return states.DRAFT()
    elif stateString == ProcessStatusAsString.SERVICE_IN_PROGRESS:
        return states.SERVICE_IN_PROGRESS()
    elif stateString == ProcessStatusAsString.SERVICE_READY:
        return states.SERVICE_READY()

###############################################################################
# State Machine
#######################################################
class StateMachine(object):
    """ 
    A simple state machine that mimics the functionality of a device from a 
    high level.
    """

    ###################################################
    def __init__(self, initialAsStr:str="",initialAsInt:int=-1):
        """ 
        Initialize the components. 

        :param initial: The initial state, given as ProcessStatusAsString
        :type initial: str
        
        """

        # Start with a default state.
        if initialAsStr != "":
            self.state = returnCorrectState(initialAsStr)
        elif initialAsInt != -1:
            self.state = returnCorrectState(processStatusFromIntToStr(initialAsInt))
        else:
            self.state = states.DRAFT()

    ###################################################
    def onUpdateEvent(self, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        """
        If the conditions are met, the status code is updated
        
        :param interface: The session or database interface
        :type interface: ProcessManagementSession | ProcessManagementBase
        :param process: The process object
        :type process: Process | ProcessInterface
        """

        # The next state will be the result of the onEvent function.
        self.state = self.state.onUpdateEvent(interface, process)
    ###################################################
    def onButtonEvent(self, event:str):
        """
        A button was pressed, advance state accordingly

        :param event: The button pressed, as ProcessStatusAsString
        :type event: str

        """
        self.state = self.state.onButtonEvent(event)


#######################################################
class State(ABC):
    """
    Abstract State class providing the implementation interface
    """

    statusCode = 0

    ###################################################
    def __init__(self):
        print('Processing current state:', str(self))

    ###################################################
    def buttons(self) -> list:
        """
        Which buttons should be shown in this state
        """
        pass

    ###################################################
    def onUpdateEvent(self, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        """
        Handle events that are delegated to this State.

        :param interface: The session or database interface
        :type interface: ProcessManagementSession | ProcessManagementBase
        :param process: The process object
        :type process: Process | ProcessInterface
        :return: Same or next object in state machine
        :rtype: State Object

        """
        pass

    ###################################################
    def onButtonEvent(self, event:str):
        """
        A button was pressed, advance state accordingly

        :param event: The button pressed, as ProcessStatusAsString
        :type event: str
        :return: Same or next object in state machine
        :rtype: State Object

        """
        pass


    ###################################################
    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.

        """
        return self.__str__()

    ###################################################
    def __str__(self):
        """
        Returns the name of the State.

        """
        return self.__class__.__name__
