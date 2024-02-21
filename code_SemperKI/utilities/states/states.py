from __future__ import annotations 

import logging

from abc import ABC, abstractmethod

from Generic_Backend.code_General.utilities.basics import Logging

import code_SemperKI.handlers.projectAndProcessManagement as PPManagement
import code_SemperKI.connections.content.session as SessionInterface
import code_SemperKI.connections.content.postgresql.pgProcesses as DBInterface
import code_SemperKI.modelFiles.processModel as ProcessModel
import code_SemperKI.serviceManager as ServiceManager

from .stateDescriptions import *

from ...definitions import ProcessDescription, ProcessUpdates, SessionContentSemperKI, ProcessDescription

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")


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
        return DRAFT()
    elif stateString == ProcessStatusAsString.SERVICE_IN_PROGRESS:
        return SERVICE_IN_PROGRESS()
    elif stateString == ProcessStatusAsString.SERVICE_READY:
        return SERVICE_READY()

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
            self.state = DRAFT()

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
    transitions = []

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
        try:
            returnState = self
            for t in self.transitions:
                resultOfTransition = t(self, interface, process)
                if resultOfTransition != self:
                    returnState = resultOfTransition
                    interface.updateProcess(process.project.projectID, process.processID, ProcessUpdates.processStatus, returnState.statusCode, process.client)
                    break #TODO: Ensure that only one transition is possible 
            
            return returnState
        except (Exception) as error:
            loggerError.error(f"{self.__str__} {self.onUpdateEvent.__name__}: {str(error)}")
            return self

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

###############################################################################
# States
#######################################################
class DRAFT(State):
    """
    The draft state, default
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.DRAFT)

    ###################################################
    def buttons(self) -> list:
        """
        None
        """
        return []

    ###################################################
    # Transitions
    def to_SERVICE_IN_PROGRESS(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> DRAFT | SERVICE_IN_PROGRESS:
        """
        Check if service has been chosen

        """
        if process.serviceType != ServiceManager.serviceManager.getNone():
            return SERVICE_IN_PROGRESS()
        return self

    ###################################################
    transitions = [to_SERVICE_IN_PROGRESS]

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        super().onUpdateEvent(interface,process)
    
    ###################################################
    def onButtonEvent(self, event: str):
        try:
            return self
        except (Exception) as error:
            loggerError.error(f"DRAFT onButtonEvent: {str(error)}")
            return self
    
    
#######################################################
class SERVICE_IN_PROGRESS(State):
    """
    The service is being edited
    
    """
    
    statusCode = processStatusAsInt(ProcessStatusAsString.SERVICE_IN_PROGRESS)
    
    ###################################################
    def buttons(self) -> list:
        """
        Back to draft

        """
        return [
            {
                "title": ButtonLabels.BACK,
                "icon": IconType.ArrowBackIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "backstepStatus",
                        "targetStatus": ProcessStatusAsString.DRAFT,
                    },
                },
                "active": True,
                "buttonVariant": ButtonTypes.secondary,
                "showIn": "process",
            },
            {
                "title": ButtonLabels.DELETE,
                "icon": IconType.DeleteIcon,
                "action": {
                    "type": "request",
                    "data": { "type": "deleteProcess" },
                },
                "active": True,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "project",
            }
        ]

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        try:
            if ServiceManager.serviceManager.getService(process.serviceType).serviceReady(process.serviceDetails):
                interface.updateProcess(process.project.projectID, process.processID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.SERVICE_READY), process.client)
                return SERVICE_READY()
            else:
                return self
        except (Exception) as error:
            loggerError.error(f"SERVICE_IN_PROGRESS onUpdateEvent: {str(error)}")
            return self
        
    ###################################################
    def onButtonEvent(self, event: str):
        try:
            return self
        except (Exception) as error:
            loggerError.error(f"SERVICE_IN_PROGRESS onButtonEvent: {str(error)}")
            return self

#######################################################
class SERVICE_READY(State):
    """
    Service is ready
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.SERVICE_READY)

    ###################################################
    def buttons(self) -> list:
        """
        Choose contractor

        """
        return [
            {
                "title": ButtonLabels.BACK,
                "icon": IconType.ArrowBackIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "backstepStatus",
                        "targetStatus": ProcessStatusAsString.DRAFT,
                    },
                },
                "active": True,
                "buttonVariant": ButtonTypes.secondary,
                "showIn": "process",
            },
            {
                "title": ButtonLabels.DELETE,
                "icon": IconType.DeleteIcon,
                "action": {
                    "type": "request",
                    "data": { "type": "deleteProcess" },
                },
                "active": True,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "project",
            },
            {
                "title": ButtonLabels.CONTRACTOR_SELECTED,
                "icon": IconType.FactoryIcon,
                "action": {
                    "type": "navigation",
                    "to": ProcessStatusAsString.CONTRACTOR_SELECTED,
                },
                "active": True,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "both",
            }
        ] 

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        try:
            return self
        except (Exception) as error:
            loggerError.error(f"SERVICE_READY onUpdateEvent: {str(error)}")
            return self

    ###################################################
    def onButtonEvent(self, event: str):
        try:
            return self
        except (Exception) as error:
            loggerError.error(f"SERVICE_READY onButtonEvent: {str(error)}")
            return self