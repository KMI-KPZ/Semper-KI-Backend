"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Contains the state machine and fellow classes
"""

import enum

from abc import ABC, abstractmethod

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactylAsDefined

#######################################################
class ProcessStatus(StrEnumExactylAsDefined):
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

#######################################################
class StateMachine(object):
    """ 
    A simple state machine that mimics the functionality of a device from a 
    high level.
    """

    def __init__(self):
        """ 
        Initialize the components. 
        
        """

        # Start with a default state.
        self.state = DRAFT()

    def onEvent(self, event):
        """
        This is the bread and butter of the state machine. Incoming events are
        delegated to the given states which then handle the event. The result is
        then assigned as the new state.
        
        """

        # The next state will be the result of the onEvent function.
        self.state = self.state.onEvent(event)

#######################################################
class State(ABC):
    """
    Abstract State class providing the implementation interface
    """

    def __init__(self):
        print('Processing current state:', str(self))

    def onEvent(self, event):
        """
        Handle events that are delegated to this State.

        """
        pass

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.

        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.

        """
        return self.__class__.__name__

# TODO
#######################################################
class DRAFT(State):
    """
    The draft state, default
    """

    def onEvent(self, event):
        if event == ProcessStatus.SERVICE_READY:
            return SERVICE_READY()

        return self

#######################################################
class SERVICE_READY(State):
    """
    Service is ready
    """

    def onEvent(self, event):
        if event == ProcessStatus.CANCELED:
            return DRAFT()

        return self
