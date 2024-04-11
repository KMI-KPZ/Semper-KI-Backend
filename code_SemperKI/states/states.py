from __future__ import annotations 
"""
Part of Semper-KI software

Silvio Weging 2024

Contains: State machine with states
"""


import logging

from abc import ABC, abstractmethod

from Generic_Backend.code_General.utilities.basics import Logging
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase, ProfileManagementOrganization, ProfileManagementUser, profileManagement, SessionContent

import code_SemperKI.handlers.projectAndProcessManagement as PPManagement
import code_SemperKI.connections.content.session as SessionInterface
import code_SemperKI.connections.content.postgresql.pgProcesses as DBInterface
import code_SemperKI.modelFiles.processModel as ProcessModel
import code_SemperKI.serviceManager as ServiceManager
import code_SemperKI.tasks.processTasks as ProcessTasks
import code_SemperKI.utilities.locales as Locales

from .stateDescriptions import *

from ..definitions import ProcessDescription, ProcessUpdates, SessionContentSemperKI, ProcessDetails

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")


###############################################################################
# Functions
#######################################################
def addButtonsToProcess(projectObj, client=True, admin=False) -> None: #is changed in place
    """
    Look at process status of every process of a project and add respective buttons

    :param projectObj: The project object containing all processes
    :type projectObj: Project | ProjectInterface
    :param client: Whether the current user is the client or the contractor
    :type client: Bool
    :param admin: Whether the current user is an admin (which may see all buttons) or not
    :type admin: Bool
    :return: Nothing
    :rtype: None

    """

    for process in projectObj[SessionContentSemperKI.processes]:
        processStatusAsString = processStatusFromIntToStr(process[ProcessDescription.processStatus])
        process["processStatusButtons"] = stateDict[processStatusAsString].buttons(client, admin)

#######################################################
def signalCompleteToDependentProcesses(interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, processObj:ProcessModel.Process|ProcessModel.ProcessInterface) -> None:
    """
    If a state transitions to completed, signal all dependent processes, that this happened.

    :param interface: The session or database interface
    :type interface: ProcessManagementSession | ProcessManagementBase
    :param processObj: The current process
    :type processObj: Process | ProcessInterface
    :return: Nothing
    :rtype: None
    
    """
    try:
        dependenciesIn, dependenciesOut = interface.getProcessDependencies(processObj.project.projectID, processObj.processID)
        for dependendProcess in dependenciesOut:
            if processStatusFromIntToStr(dependendProcess.processStatus) == ProcessStatusAsString.WAITING_FOR_OTHER_PROCESS:
                currentStateMachine = StateMachine(initialAsInt=dependendProcess.processStatus)
                currentStateMachine.onUpdateEvent(interface, dependendProcess)
        
        return
    except Exception as error:
        loggerError.error(f"Error when updating dependent processes: {error}")

#######################################################
def signalDependencyToOtherProcesses(interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, processObj:ProcessModel.Process|ProcessModel.ProcessInterface) -> None:
    """
    If a process adds a dependency, signal all dependent processes, that this happened.

    :param interface: The session or database interface
    :type interface: ProcessManagementSession | ProcessManagementBase
    :param processObj: The current process
    :type processObj: Process | ProcessInterface
    :return: Nothing
    :rtype: None
    
    """
    try:
        
        dependenciesIn, dependenciesOut = interface.getProcessDependencies(processObj.project.projectID, processObj.processID)
        for dependendProcess in dependenciesOut:
            currentStateMachine = StateMachine(initialAsInt=dependendProcess.processStatus)
            currentStateMachine.onUpdateEvent(interface, dependendProcess)
            
        return
    except Exception as error:
        loggerError.error(f"Error when updating dependent processes: {error}")



stateDict = {} # will later contain mapping from string to instance of every state
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
            self.state = stateDict[initialAsStr]
        elif initialAsInt != -1:
            self.state = stateDict[processStatusFromIntToStr(initialAsInt)]
        else:
            self.state = stateDict[ProcessStatusAsString.DRAFT]

    ###################################################
    def showPaths(self):
        """
        Show the paths that this machine can take
        
        """
        try:
            outDict = {"nodes": [], "edges": []}
            edgeID = -1

            for node in stateDict:
                outDict["nodes"].append({"id": node})

                for transition in stateDict[node].updateTransitions:
                    edgeID += 1
                    transitionTypesArr = transition.__annotations__["return"].split("|")
                    if len(transitionTypesArr) == 2:
                        source = transitionTypesArr[0].rstrip(" ")
                        target = transitionTypesArr[1].lstrip(" ")
                        outDict["edges"].append({"id": edgeID, "source": source, "target": target})
                    elif len(transitionTypesArr) > 2:
                        source = transitionTypesArr[0].rstrip(" ")
                        for entryIdx in range(1,len(transitionTypesArr)):
                            target = transitionTypesArr[entryIdx].lstrip(" ").rstrip(" ")
                            outDict["edges"].append({"id": edgeID, "source": source, "target": target})
                            edgeID += 1
                    else:
                        source = node
                        target = transitionTypesArr[0].rstrip(" ")
                        outDict["edges"].append({"id": edgeID, "source": source, "target": target})
                for transitionKey in stateDict[node].buttonTransitions:
                    transition = stateDict[node].buttonTransitions[transitionKey]
                    edgeID += 1
                    transitionTypesArr = transition.__annotations__["return"].split("|")
                    if len(transitionTypesArr) == 2:
                        source = transitionTypesArr[0].rstrip(" ")
                        target = transitionTypesArr[1].lstrip(" ")
                        outDict["edges"].append({"id": edgeID, "source": source, "target": target})
                    elif len(transitionTypesArr) > 2:
                        source = transitionTypesArr[0].rstrip(" ")
                        for entryIdx in range(1,len(transitionTypesArr)):
                            target = transitionTypesArr[entryIdx].lstrip(" ").rstrip(" ")
                            outDict["edges"].append({"id": edgeID, "source": source, "target": target})
                            edgeID += 1
                    else:
                        source = node
                        target = transitionTypesArr[0].rstrip(" ")
                        outDict["edges"].append({"id": edgeID, "source": source, "target": target})

            return outDict
        except Exception as e:
            print(node, e)
            return outDict

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
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        """
        A button was pressed, advance state accordingly

        :param event: The button pressed, as ProcessStatusAsString
        :type event: str

        """
        self.state = self.state.onButtonEvent(event, interface, process)


#######################################################
class State(ABC):
    """
    Abstract State class providing the implementation interface
    """

    statusCode = 0

    ###################################################
    def __init__(self):
        #print('Processing current state:', str(self))
        pass

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Which buttons should be shown in this state
        """
        pass

    ###################################################
    updateTransitions = []
    buttonTransitions = {}

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
            for t in self.updateTransitions:
                resultOfTransition = t(self, interface, process)
                if resultOfTransition != self:
                    returnState = resultOfTransition
                    interface.updateProcess(process.project.projectID, process.processID, ProcessUpdates.processStatus, returnState.statusCode, process.client)
                    PPManagement.fireWebsocketEvents(process.project.projectID, [process.processID], interface.getSession(), ProcessUpdates.processStatus)
                    break #TODO: Ensure that only one transition is possible 
            
            return returnState
        except (Exception) as error:
            loggerError.error(f"{self.__str__} {self.onUpdateEvent.__name__}: {str(error)}")
            return self

    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        """
        A button was pressed, advance state accordingly

        :param event: The button pressed, as ProcessStatusAsString
        :type event: str
        :param interface: The session or database interface
        :type interface: ProcessManagementSession | ProcessManagementBase
        :param process: The process object
        :type process: Process | ProcessInterface
        :return: Same or next object in state machine
        :rtype: State Object

        """
        try:
            returnState = self
            for t in self.buttonTransitions:
                if event == t:
                    returnState = self.buttonTransitions[t](self, interface, process)
                    interface.updateProcess(process.project.projectID, process.processID, ProcessUpdates.processStatus, returnState.statusCode, process.client)
                    PPManagement.fireWebsocketEvents(process.project.projectID, [process.processID], interface.getSession(), ProcessUpdates.processStatus)
                    break #TODO: Ensure that only one transition is possible 
            
            return returnState
        except (Exception) as error:
            loggerError.error(f"{self.__str__} {self.onButtonEvent.__name__}: {str(error)}")
            return self

    ###################################################
    def sendMailToClient(self, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface, locale:str, reason:str, message:str):
        """
        Send a mail to the client

        :param interface: The session or database interface
        :type interface: ProcessManagementSession | ProcessManagementBase
        :param process: The process object
        :type process: Process | ProcessInterface
        :param locale: The locale string for that user
        :type locale: str
        :param reason: What is the reason for the mail
        :type reason: str
        :param message: The content of the message
        :type message: str
        :return: Nothing
        :rtype: None
        
        """
        # Send mail to client
        if ProfileManagementBase.checkIfHashIDBelongsToOrganization(process.client):
            clientMail = ProfileManagementOrganization.getEMailAddress(process.client)
        else:
            clientMail = ProfileManagementUser.getEMailAddress(process.client)
        clientName = ProfileManagementBase.getUserNameViaHash(process.client)
        processTitle = process.processDetails[ProcessDetails.title] if ProcessDetails.title in process.processDetails else process.processID
        ProcessTasks.sendEMail(clientMail, f"{reason} '{processTitle}'", clientName, locale, message)
        
    ###################################################
    def sendMailToContractor(self, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface, locale:str, reason:str, message:str):
        """
        Send a mail to the contractor

        :param interface: The session or database interface
        :type interface: ProcessManagementSession | ProcessManagementBase
        :param process: The process object
        :type process: Process | ProcessInterface
        :param locale: The locale string for that user
        :type locale: str
        :param reason: What is the reason for the mail
        :type reason: str
        :param message: The content of the message
        :type message: str
        :return: Nothing
        :rtype: None
        
        """
        # Send mail to contractor
        contractorMail = ProfileManagementOrganization.getEMailAddress(process.contractor.hashedID)
        contracorName = ProfileManagementBase.getUserNameViaHash(process.contractor.hashedID)
        processTitle = process.processDetails[ProcessDetails.title] if ProcessDetails.title in process.processDetails else process.processID
        ProcessTasks.sendEMail(contractorMail, f"{reason} '{processTitle}'", contracorName, locale, message)
        

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
    name = ProcessStatusAsString.DRAFT

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        None
        """
        return [{
                "title": ButtonLabels.DELETE,
                "icon": IconType.DeleteIcon,
                "action": {
                    "type": "request",
                    "data": { "type": "deleteProcess" },
                },
                "active": True,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "project",
            }]

    ###################################################
    # Transitions
    ###################################################
    def to_SERVICE_IN_PROGRESS(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DRAFT | SERVICE_IN_PROGRESS:
        """
        Check if service has been chosen

        """
        if process.serviceType != ServiceManager.serviceManager.getNone():
            return stateDict[ProcessStatusAsString.SERVICE_IN_PROGRESS]
        return self

    ###################################################
    def to_WAITING_FOR_OTHER_PROCESS(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DRAFT | WAITING_FOR_OTHER_PROCESS:
        """
        Check if other process exists before this one

        """
        dependenciesIn, dependenciesOut = interface.getProcessDependencies(process.project.projectID, process.processID)
 
        for priorProcess in dependenciesIn: 
            if priorProcess.processStatus < processStatusAsInt(ProcessStatusAsString.COMPLETED):
                return stateDict[ProcessStatusAsString.WAITING_FOR_OTHER_PROCESS] # there are processes that this one depends on and they're not finished (yet)
        return self # either all prior processes have been completed or there are none

    ###################################################
    updateTransitions = [to_SERVICE_IN_PROGRESS, to_WAITING_FOR_OTHER_PROCESS]
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process)
    
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process)
    
#######################################################
class SERVICE_IN_PROGRESS(State):
    """
    The service is being edited
    
    """
    
    statusCode = processStatusAsInt(ProcessStatusAsString.SERVICE_IN_PROGRESS)
    name = ProcessStatusAsString.SERVICE_IN_PROGRESS
    
    ###################################################
    def buttons(self, client=True, admin=False) -> list:
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
    # Transitions

    ###################################################
    def to_DRAFT(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
        DRAFT:
        """
        Button was pressed, clean up and go back

        """
        serviceContent = process.serviceDetails
        interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.serviceDetails, serviceContent, process.client)
        interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.serviceType, {}, process.client)
        return stateDict[ProcessStatusAsString.DRAFT]

    ###################################################
    def to_SERVICE_READY(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          SERVICE_IN_PROGRESS | SERVICE_READY:
        """
        Check if service has been fully defined

        """
        if process.serviceType != ServiceManager.serviceManager.getNone() and ServiceManager.serviceManager.getService(process.serviceType).serviceReady(process.serviceDetails):
            return stateDict[ProcessStatusAsString.SERVICE_READY]
        return self
    
    ###################################################
    def to_SERVICE_COMPLICATION(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          SERVICE_IN_PROGRESS | SERVICE_COMPLICATION:
        """
        Service Conditions not OK

        """
        if ServiceManager.serviceManager.getService(process.serviceType).checkIfSelectionIsAvailable(process):
            return self
        else:
            return stateDict[ProcessStatusAsString.SERVICE_COMPLICATION]
    
    ###################################################
    def to_WAITING_FOR_OTHER_PROCESS(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          SERVICE_IN_PROGRESS | WAITING_FOR_OTHER_PROCESS:
        """
        Check if other process exists before this one

        """
        dependenciesIn, dependenciesOut = interface.getProcessDependencies(process.project.projectID, process.processID)
        for priorProcess in dependenciesIn:
            if priorProcess.processStatus < processStatusAsInt(ProcessStatusAsString.COMPLETED):
                return stateDict[ProcessStatusAsString.WAITING_FOR_OTHER_PROCESS]
        return self # either all prior processes have been completed or there are none
            

    ###################################################
    updateTransitions = [to_WAITING_FOR_OTHER_PROCESS, to_SERVICE_COMPLICATION, to_SERVICE_READY]
    buttonTransitions = {ProcessStatusAsString.DRAFT: to_DRAFT}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process)
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process)

#######################################################
class SERVICE_READY(State):
    """
    Service is ready
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.SERVICE_READY)
    name = ProcessStatusAsString.SERVICE_READY

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
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
                    "to": "contractorSelection",
                },
                "active": True,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "both",
            }
        ] 
    
    ###################################################
    # Transitions
    ###################################################
    def to_CONTRACTOR_SELECTED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
        SERVICE_READY | CONTRACTOR_SELECTED:
        """
        Contractor was Selected

        """
        if ProcessDetails.provisionalContractor in process.processDetails and process.processDetails[ProcessDetails.provisionalContractor] != "":
            return stateDict[ProcessStatusAsString.CONTRACTOR_SELECTED]
        return self
    
    ###################################################
    def to_SERVICE_COMPLICATION(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          SERVICE_IN_PROGRESS | SERVICE_COMPLICATION:
        """
        Service Conditions not OK

        """
        if ServiceManager.serviceManager.getService(process.serviceType).checkIfSelectionIsAvailable(process):
            return self
        else:
            return stateDict[ProcessStatusAsString.SERVICE_COMPLICATION]
    
    ###################################################
    def to_DRAFT(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
        DRAFT:
        """
        Button was pressed, clean up and go back

        """
        serviceContent = process.serviceDetails
        #interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.processDetails, process.processDetails, process.client)
        interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.serviceDetails, serviceContent, process.client)
        interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.serviceType, {}, process.client)
        return stateDict[ProcessStatusAsString.DRAFT]
    
    ###################################################
    updateTransitions = [to_SERVICE_COMPLICATION, to_CONTRACTOR_SELECTED]
    buttonTransitions = {ProcessStatusAsString.DRAFT: to_DRAFT}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process)
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process)

#######################################################
class WAITING_FOR_OTHER_PROCESS(State):
    """
    Waiting for other preceding Process

    """

    statusCode = processStatusAsInt(ProcessStatusAsString.WAITING_FOR_OTHER_PROCESS)
    name = ProcessStatusAsString.WAITING_FOR_OTHER_PROCESS

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Buttons for WAITING_FOR_OTHER_PROCESS

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
                "title": ButtonLabels.DELETE, # do not change
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
    # Transitions
    ###################################################
    def to_SERVICE_READY(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          WAITING_FOR_OTHER_PROCESS | SERVICE_READY:
        """
        Check if service has been fully defined

        """
        dependenciesIn, dependenciesOut = interface.getProcessDependencies(process.project.projectID, process.processID)
        for priorProcess in dependenciesIn:
            if priorProcess.processStatus < processStatusAsInt(ProcessStatusAsString.COMPLETED):
                return self # there are processes that this one depends on and they're not finished (yet)

        if process.serviceType != ServiceManager.serviceManager.getNone() and ServiceManager.serviceManager.getService(process.serviceType).serviceReady(process.serviceDetails):
            return stateDict[ProcessStatusAsString.SERVICE_READY]
        return self

    ###################################################
    def to_SERVICE_IN_PROGRESS(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          WAITING_FOR_OTHER_PROCESS | SERVICE_IN_PROGRESS:
        """
        From: WAITING_FORT_OTHER_PROGRESS
        To: SERVICE_IN_PROGRESS

        Must be triggered from the outside, for example when a process is finished, it signals all outgoing dependend processes of this
        """
        dependenciesIn, dependenciesOut = interface.getProcessDependencies(process.project.projectID, process.processID)
        for priorProcess in dependenciesIn:
            if priorProcess.processStatus < processStatusAsInt(ProcessStatusAsString.COMPLETED):
                return self
        
        if process.serviceType != ServiceManager.serviceManager.getNone():
            return stateDict[ProcessStatusAsString.SERVICE_IN_PROGRESS] 
        return self
    
    ###################################################
    def to_DRAFT(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          WAITING_FOR_OTHER_PROCESS | DRAFT:
        """
        If no service was selected, return to draft after dependency was fulfilled

        """
        dependenciesIn, dependenciesOut = interface.getProcessDependencies(process.project.projectID, process.processID)

        for priorProcess in dependenciesIn:
            if priorProcess.processStatus < processStatusAsInt(ProcessStatusAsString.COMPLETED):
                return self # there are processes that this one depends on and they're not finished (yet)
        
        if process.serviceType == ServiceManager.serviceManager.getNone():
            return stateDict[ProcessStatusAsString.DRAFT]
        return self

    ###################################################
    def to_DRAFT_viaButton(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DRAFT:
        """
        To: DRAFT
        
        """
        serviceContent = process.serviceDetails
        interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.processDetails, process.processDetails, process.client)
        interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.serviceDetails, serviceContent, process.client)
        interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.serviceType, {}, process.client)
        return stateDict[ProcessStatusAsString.DRAFT]

    ###################################################
    updateTransitions = [to_SERVICE_READY, to_SERVICE_IN_PROGRESS, to_DRAFT]
    buttonTransitions = {ProcessStatusAsString.DRAFT: to_DRAFT_viaButton}
    
    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class SERVICE_COMPLICATION(State):
    """
    Service Complication happened

    """

    statusCode = processStatusAsInt(ProcessStatusAsString.SERVICE_COMPLICATION)
    name = ProcessStatusAsString.SERVICE_COMPLICATION

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Back to Draft

        """
        return [
            {
                "title": ButtonLabels.DELETE, # do not change
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
                "title": ButtonLabels.SERVICE_COMPLICATION,
                "icon": IconType.TroubleshootIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "forwardStatus",
                        "targetStatus": ProcessStatusAsString.SERVICE_IN_PROGRESS,
                    },
                },
                "active": True,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "both",
            },
        ] 
    
    ###################################################
    # Transitions
    ###################################################
    # def to_DRAFT(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
    #       DRAFT:
    #     """
    #     To: Draft
        
    #     """
    #     serviceContent = process.serviceDetails
    #     #interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.processDetails, process.processDetails, process.client)
    #     interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.serviceDetails, serviceContent, process.client)
    #     interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.serviceType, {}, process.client)
    #     return stateDict[ProcessStatusAsString.DRAFT]

    ###################################################
    def to_SERVICE_IN_PROGRESS(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          SERVICE_COMPLICATION | SERVICE_IN_PROGRESS | SERVICE_READY:
        """
        From: SERVICE_COMPLICATION
        To: SERVICE_IN_PROGRESS | SERVICE_READY

        """
        if ServiceManager.serviceManager.getService(process.serviceType).checkIfSelectionIsAvailable(process):
            if process.serviceType != ServiceManager.serviceManager.getNone() and ServiceManager.serviceManager.getService(process.serviceType).serviceReady(process.serviceDetails):
                return stateDict[ProcessStatusAsString.SERVICE_READY]
            else:
                return stateDict[ProcessStatusAsString.SERVICE_IN_PROGRESS]
        else:
            return self
    
    ###################################################
    updateTransitions = [] # TODO add functions that are called on update, leave empty if none exist
    buttonTransitions = {ProcessStatusAsString.SERVICE_IN_PROGRESS: to_SERVICE_IN_PROGRESS}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class CONTRACTOR_SELECTED(State):
    """
    Contractor has been chosen
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.CONTRACTOR_SELECTED)
    name = ProcessStatusAsString.CONTRACTOR_SELECTED

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Buttons for  CONTRACTOR_SELECTED

        """
        return [
            {
                "title": ButtonLabels.BACK,
                "icon": IconType.ArrowBackIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "backstepStatus",
                        "targetStatus": ProcessStatusAsString.SERVICE_READY,
                    },
                },
                "active": True,
                "buttonVariant": ButtonTypes.secondary,
                "showIn": "process",
            },
            {
                "title": ButtonLabels.DELETE, # do not change
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
                "title": ButtonLabels.VERIFYING,
                "icon": IconType.TaskIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "forwardStatus",
                        "targetStatus": ProcessStatusAsString.VERIFYING,
                    },
                },
                "active": True,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "both",
            }
        ] 
    
    ###################################################
    # Transitions
    ###################################################
    def to_VERIFYING(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CONTRACTOR_SELECTED | VERIFYING: # TODO: Change to current and next state
        """
        From: CONTRACTOR_SELECTED
        To: VERIFYING

        """
        interface.verifyProcess(process, interface.getSession() , interface.getUserID())
        return stateDict[ProcessStatusAsString.VERIFYING]

    ###################################################
    def to_SERVICE_READY(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          SERVICE_READY:
        """
        To: SERVICE_READY
        
        """
        interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.processDetails, {ProcessDetails.provisionalContractor: ""}, process.client)
        return stateDict[ProcessStatusAsString.SERVICE_READY]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.SERVICE_READY: to_SERVICE_READY, ProcessStatusAsString.VERIFYING: to_VERIFYING}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class VERIFYING(State):
    """
    Process is currently being verified

    """

    statusCode = processStatusAsInt(ProcessStatusAsString.VERIFYING)
    name = ProcessStatusAsString.VERIFYING

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Buttons for VERIFYING

        """
        return [
            {
                "title": ButtonLabels.BACK,
                "icon": IconType.ArrowBackIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "backstepStatus",
                        "targetStatus": ProcessStatusAsString.CONTRACTOR_SELECTED,
                    },
                },
                "active": True,
                "buttonVariant": ButtonTypes.secondary,
                "showIn": "process",
            },
            {
                "title": ButtonLabels.DELETE, # do not change
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
    # Transitions
    ###################################################
    def to_VERIFIED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          VERIFYING | VERIFIED:
        """
        From: VERIFYING
        To: VERIFIED

        """
        # TODO Can only be set by admins (admins need to see buttons)

        return stateDict[ProcessStatusAsString.VERIFIED]

    ###################################################
    def to_CONTRACTOR_SELECTED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CONTRACTOR_SELECTED:
        """
        To: CONTRACTOR_SELECTED
        
        """
        # TODO Cancel verification
        return stateDict[ProcessStatusAsString.CONTRACTOR_SELECTED]

    ###################################################
    updateTransitions = [to_VERIFIED]
    buttonTransitions = {ProcessStatusAsString.CONTRACTOR_SELECTED: to_CONTRACTOR_SELECTED }

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class VERIFIED(State):
    """
    Process has been verified
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.VERIFIED)
    name = ProcessStatusAsString.VERIFIED

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Manual Request

        """
        return [
            {
                "title": ButtonLabels.BACK,
                "icon": IconType.ArrowBackIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "backstepStatus",
                        "targetStatus": ProcessStatusAsString.CONTRACTOR_SELECTED,
                    },
                },
                "active": True,
                "buttonVariant": ButtonTypes.secondary,
                "showIn": "process",
            },
            {
                "title": ButtonLabels.DELETE, # do not change
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
                "title": ButtonLabels.REQUESTED,
                "icon": IconType.MailIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "forwardStatus",
                        "targetStatus": ProcessStatusAsString.REQUESTED,
                    },
                },
                "active": True,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "both",
            }
        ] 
    
    ###################################################
    # Transitions
    ###################################################
    def to_REQUESTED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          VERIFIED | REQUESTED:
        """
        From: VERIFIED
        To: REQUESTED

        Is called from the outside by a finished verification
        """
        retVal = interface.sendProcess(process, interface.getSession() , interface.getUserID())
        if isinstance(retVal, Exception):
            return stateDict[ProcessStatusAsString.VERIFIED]
        return stateDict[ProcessStatusAsString.REQUESTED]

    ###################################################
    def to_CONTRACTOR_SELECTED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CONTRACTOR_SELECTED:
        """
        To: CONTRACTOR_SELECTED
        
        """
        # TODO discard verification
        return stateDict[ProcessStatusAsString.CONTRACTOR_SELECTED]

    ###################################################
    updateTransitions = [to_REQUESTED]
    buttonTransitions = {ProcessStatusAsString.CONTRACTOR_SELECTED: to_CONTRACTOR_SELECTED, ProcessStatusAsString.REQUESTED: to_REQUESTED} # TODO add functions that are called on button click, leave empty if none exist

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class REQUESTED(State):
    """
    Contractor was informed about possible contract
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.REQUESTED)
    name = ProcessStatusAsString.REQUESTED

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Buttons for REQUESTED, no Back-Button, Contractor chooses between Confirm, Reject and Clarification
        
        """
        outArr = []
        if client or admin:
            outArr.extend([
                {
                    "title": ButtonLabels.DELETE, # do not change
                    "icon": IconType.DeleteIcon,
                    "action": {
                        "type": "request",
                        "data": { "type": "deleteProcess" },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "project",
                }
            ])
        if not client or admin: # contractor
            outArr.extend([
                {
                    "title": ButtonLabels.DELETE, # do not change
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
                    "title": ButtonLabels.CLARIFICATION,
                    "icon": IconType.QuestionAnswerIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.CLARIFICATION,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.CONFIRMED_BY_CONTRACTOR,
                    "icon": IconType.DoneAllIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.CONFIRMED_BY_CONTRACTOR,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.REJECTED_BY_CONTRACTOR,
                    "icon": IconType.CancelIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.REJECTED_BY_CONTRACTOR,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                }
            ])
        return outArr
    
    ###################################################
    # Transitions
    ###################################################
    def to_CLARIFICATION(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          REQUESTED | CLARIFICATION: 
        """
        From: REQUESTED
        To: CLARIFICATION

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","questionsFromContractor"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","questionsFromContractor"])
        self.sendMailToClient(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.CLARIFICATION]

    ###################################################
    def to_CONFIRMED_BY_CONTRACTOR(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          REQUESTED | CONFIRMED_BY_CONTRACTOR:
        """
        From: REQUESTED
        To: CONFIRMED_BY_CONTRACTOR

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","confirmedByContractor"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","confirmedByContractor"])
        self.sendMailToClient(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.CONFIRMED_BY_CONTRACTOR]

    ###################################################
    def to_REJECTED_BY_CONTRACTOR(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          REQUESTED | REJECTED_BY_CONTRACTOR:
        """
        From: REQUESTED
        To: REJECTED_BY_CONTRACTOR

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","declinedByContractor"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","declinedByContractor"])
        self.sendMailToClient(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.REJECTED_BY_CONTRACTOR]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.CLARIFICATION: to_CLARIFICATION, ProcessStatusAsString.CONFIRMED_BY_CONTRACTOR: to_CONFIRMED_BY_CONTRACTOR, ProcessStatusAsString.REJECTED_BY_CONTRACTOR: to_REJECTED_BY_CONTRACTOR}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class CLARIFICATION(State):
    """
    Clarification needed by Contractor

    """

    statusCode = processStatusAsInt(ProcessStatusAsString.CLARIFICATION)
    name = ProcessStatusAsString.CLARIFICATION

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Buttons for CLARIFICATION

        """
        outArr = []
        if client or admin:
            outArr.extend([
                {
                    "title": ButtonLabels.DELETE, # do not change
                    "icon": IconType.DeleteIcon,
                    "action": {
                        "type": "request",
                        "data": { "type": "deleteProcess" },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "project",
                },
            ])
        if not client or admin:
            outArr.extend([
                {
                    "title": ButtonLabels.CONFIRMED_BY_CONTRACTOR,
                    "icon": IconType.DoneAllIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.CONFIRMED_BY_CONTRACTOR,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.REJECTED_BY_CONTRACTOR,
                    "icon": IconType.CancelIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.REJECTED_BY_CONTRACTOR,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                }
            ])
        return outArr
    
    ###################################################
    # Transitions
    ###################################################
    def to_CONFIRMED_BY_CONTRACTOR(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CLARIFICATION | CONFIRMED_BY_CONTRACTOR:
        """
        From: CLARIFICATION
        To: CONFIRMED_BY_CONTRACTOR

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","confirmedByContractor"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","confirmedByContractor"])
        self.sendMailToClient(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.CONFIRMED_BY_CONTRACTOR]

    ###################################################
    def to_REJECTED_BY_CONTRACTOR(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CLARIFICATION | REJECTED_BY_CONTRACTOR:
        """
        From: CLARIFICATION
        To: REJECTED_BY_CONTRACTOR

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","declinedByContractor"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","declinedByContractor"])
        self.sendMailToClient(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.REJECTED_BY_CONTRACTOR]

    ###################################################
    updateTransitions = [] # TODO add functions that are called on update, leave empty if none exist
    buttonTransitions = {ProcessStatusAsString.CONFIRMED_BY_CONTRACTOR: to_CONFIRMED_BY_CONTRACTOR, ProcessStatusAsString.REJECTED_BY_CONTRACTOR: to_REJECTED_BY_CONTRACTOR} # TODO add functions that are called on button click, leave empty if none exist

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class CONFIRMED_BY_CONTRACTOR(State):
    """
    Order Confirmed by Contractor
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.CONFIRMED_BY_CONTRACTOR)
    name = ProcessStatusAsString.CONFIRMED_BY_CONTRACTOR

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Buttons for CONFIRMED_BY_CONTRACTOR, no Back-Button

        """
        outArr = []
        if client or admin:
            outArr.extend([
                {
                    "title": ButtonLabels.DELETE, # do not change
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
                    "title": ButtonLabels.CONFIRMED_BY_CLIENT,
                    "icon": IconType.DoneAllIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.CONFIRMED_BY_CLIENT,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.REJECTED_BY_CLIENT,
                    "icon": IconType.CancelIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.REJECTED_BY_CLIENT,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                }
            ])
        if not client or admin:
            outArr.extend(
            [
            ])
        return outArr

    ###################################################
    # Transitions
    ###################################################
    def to_CONFIRMED_BY_CLIENT(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CONFIRMED_BY_CONTRACTOR | CONFIRMED_BY_CLIENT:
        """
        From: CONFIRMED_BY_CONTRACTOR
        To: CONFIRMED_BY_CLIENT

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.contractor.hashedID)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","confirmedByClient"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","confirmedByClient"])
        self.sendMailToContractor(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.CONFIRMED_BY_CLIENT]

    ###################################################
    def to_REJECTED_BY_CLIENT(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CONFIRMED_BY_CONTRACTOR | REJECTED_BY_CLIENT:
        """
        From: CONFIRMED_BY_CONTRACTOR
        To: REJECTED_BY_CLIENT

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.contractor.hashedID)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","declinedByClient"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","declinedByClient"])
        self.sendMailToContractor(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.REJECTED_BY_CLIENT]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.CONFIRMED_BY_CLIENT: to_CONFIRMED_BY_CLIENT, ProcessStatusAsString.REJECTED_BY_CLIENT: to_REJECTED_BY_CLIENT}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class REJECTED_BY_CONTRACTOR(State):
    """
    Order Rejected by Contractor
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.REJECTED_BY_CONTRACTOR)
    name = ProcessStatusAsString.REJECTED_BY_CONTRACTOR

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        No Buttons only CANCELED

        """
        outArr = []
        if client or admin:
            outArr.extend( [
                {
                    "title": ButtonLabels.DELETE, # do not change
                    "icon": IconType.DeleteIcon,
                    "action": {
                        "type": "request",
                        "data": { "type": "deleteProcess" },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "project",
                }
            ] )
        if not client or admin:
            outArr.extend([

            ])
        return outArr
    
    ###################################################
    # Transitions
    ###################################################
    def to_CANCELED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          REJECTED_BY_CONTRACTOR | CANCELED:
        """
        From: REJECTED_BY_CONTRACTOR
        To: CANCELLED

        """
        # TODO do stuff to clean up
        return stateDict[ProcessStatusAsString.CANCELED]

    ###################################################
    updateTransitions = [to_CANCELED]
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class CONFIRMED_BY_CLIENT(State):
    """
    Order Confirmed by Client
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.CONFIRMED_BY_CLIENT)
    name = ProcessStatusAsString.CONFIRMED_BY_CLIENT

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Buttons for CONFIRMED_BY_CLIENT, no Back-Button

        """
        outArr = []
        if client or admin:
            outArr.extend( [
                {
                    "title": ButtonLabels.DELETE, # do not change
                    "icon": IconType.DeleteIcon,
                    "action": {
                        "type": "request",
                        "data": { "type": "deleteProcess" },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "project",
                },
            ])
        if not client or admin:
            outArr.extend( [
                {
                    "title": ButtonLabels.PRODUCTION,
                    "icon": IconType.FactoryIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.PRODUCTION,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                }
            ] )
        return outArr
    
    ###################################################
    # Transitions
    ###################################################
    def to_PRODUCTION(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CONFIRMED_BY_CLIENT | PRODUCTION:
        """
        From: CONFIRMED_BY_CLIENT
        To: PRODUCTION

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","inProduction"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","inProduction"])
        self.sendMailToClient(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.PRODUCTION]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.PRODUCTION: to_PRODUCTION}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class REJECTED_BY_CLIENT(State):
    """
    Order rejected by Client
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.REJECTED_BY_CLIENT)
    name = ProcessStatusAsString.REJECTED_BY_CLIENT

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        No Buttons only CANCELED

        """
        outArr = []
        if client or admin:
            outArr.extend( [
                {
                    "title": ButtonLabels.DELETE, # do not change
                    "icon": IconType.DeleteIcon,
                    "action": {
                        "type": "request",
                        "data": { "type": "deleteProcess" },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "project",
                }
            ] )
        if not client or admin:
            outArr.extend([

            ])
        return outArr
    
    ###################################################
    # Transitions
    ###################################################
    def to_CANCELED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          REJECTED_BY_CLIENT | CANCELED:
        """
        From: REJECTED_BY_CLIENT
        To: CANCELLED

        """
        # TODO clean up and stuff
        return stateDict[ProcessStatusAsString.CANCELED]

    ###################################################
    updateTransitions = [to_CANCELED]
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class PRODUCTION(State):
    """
    Order is in Production
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.PRODUCTION)
    name = ProcessStatusAsString.PRODUCTION

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Buttons for PRODUCTION, no Back-Button

        """
        outArr = []
        if client or admin:
            outArr.extend( [
            ])
        if not client or admin:
            outArr.extend( [
                {
                    "title": ButtonLabels.DELETE, # do not change
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
                    "title": ButtonLabels.DELIVERY,
                    "icon": IconType.LocalShippingIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.DELIVERY,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.FAILED,
                    "icon": IconType.CancelIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.FAILED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                }
            ] )
        return outArr
    
    ###################################################
    # Transitions
    ###################################################
    def to_DELIVERY(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          PRODUCTION | DELIVERY:
        """
        From: PRODUCTION
        To: DELIVERY

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","inDelivery"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","inDelivery"])
        self.sendMailToClient(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.DELIVERY]

    ###################################################
    def to_FAILED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          PRODUCTION | FAILED:
        """
        From: PRODUCTION
        To: FAILED

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","productionFailed"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","productionFailed"])
        self.sendMailToClient(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.FAILED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.DELIVERY: to_DELIVERY, ProcessStatusAsString.FAILED: to_FAILED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class DELIVERY(State):
    """
    Order is being delivered
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.DELIVERY)
    name = ProcessStatusAsString.DELIVERY

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Buttons for DELIVERY, no Back-Button

        """
        outArr = []
        if client or admin:
            outArr.extend( [
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
                    "title": ButtonLabels.COMPLETED,
                    "icon": IconType.DoneAllIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.DISPUTE,
                    "icon": IconType.TroubleshootIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.DISPUTE,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.FAILED,
                    "icon": IconType.CancelIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.FAILED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                }
            ] )
        if not client or admin:
            outArr.extend([

            ])
        return outArr
    ###################################################
    # Transitions
    ###################################################
    def to_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DELIVERY | COMPLETED:
        """
        From: DELIVERY
        To: COMPLETED

        """
        
        # signal to dependent processes, that this one is finished
        signalCompleteToDependentProcesses(interface, process)

        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","processFinished"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","processFinished"])
        self.sendMailToContractor(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.COMPLETED]

    ###################################################
    def to_DISPUTE(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DELIVERY | DISPUTE:
        """
        From: DELIVERY
        To: DISPUTE

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","dispute"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","dispute"])
        self.sendMailToContractor(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.DISPUTE]

    ###################################################
    def to_FAILED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DELIVERY | FAILED:
        """
        From: DELIVERY
        To: FAILED

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","failed"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","failed"])
        self.sendMailToContractor(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.FAILED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.COMPLETED: to_COMPLETED, ProcessStatusAsString.DISPUTE: to_DISPUTE, ProcessStatusAsString.FAILED: to_FAILED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class DISPUTE(State):
    """
    Dispute over Delivery
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.DISPUTE)
    name = ProcessStatusAsString.DISPUTE

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Buttons for DISPUTE, no Back-Button

        """
        outArr = []
        if client or admin:
            outArr.extend( [
                {
                    "title": ButtonLabels.DELETE, # do not change
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
                    "title": ButtonLabels.COMPLETED,
                    "icon": IconType.DoneAllIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.FAILED,
                    "icon": IconType.CancelIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.FAILED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                }
            ] )
        if not client or admin:
            outArr.extend([

            ])
        return outArr
    
    ###################################################
    # Transitions
    ###################################################
    def to_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DISPUTE | COMPLETED:
        """
        From: DISPUTE
        To: COMPLETED

        """
        # signal to dependent processes, that this one is finished
        signalCompleteToDependentProcesses(interface, process)

        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","processFinished"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","processFinished"])
        self.sendMailToContractor(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.COMPLETED]

    ###################################################
    def to_FAILED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DISPUTE | FAILED:
        """
        From: DISPUTE
        To: FAILED

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","failed"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","failed"])
        self.sendMailToContractor(interface, process, userLocale, subject, message)
        return stateDict[ProcessStatusAsString.FAILED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.COMPLETED: to_COMPLETED, ProcessStatusAsString.COMPLETED: to_FAILED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class COMPLETED(State):
    """
    Order has been completed
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.COMPLETED)
    name = ProcessStatusAsString.COMPLETED

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Delete and clone (client only)

        """
        if client or admin:
            return [
                {
                    "title": ButtonLabels.DELETE, # do not change
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
                    "title": ButtonLabels.CLONE,
                    "icon": IconType.ReplayIcon,
                    "action": {
                        "type": "request",
                        "data": { "type": "cloneProcess" },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "project",
                }
            ] 
        else:
            return []
    
    ###################################################
    # Transitions

    ###################################################
    updateTransitions = []
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class FAILED(State):
    """
    Contractor has failed the contract
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.FAILED)
    name = ProcessStatusAsString.FAILED

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Delete and clone (client only)

        """
        if client or admin:
            return [
                {
                    "title": ButtonLabels.DELETE, # do not change
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
                    "title": ButtonLabels.CLONE,
                    "icon": IconType.ReplayIcon,
                    "action": {
                        "type": "request",
                        "data": { "type": "cloneProcess" },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "project",
                }
            ] 
        else:
            return []
    
    ###################################################
    # Transitions

    ###################################################
    updateTransitions = []
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class CANCELED(State):
    """
    Order has been canceled
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.CANCELED)
    name = ProcessStatusAsString.CANCELED

    ###################################################
    def buttons(self, client=True, admin=False) -> list:
        """
        Delete and clone (client only)

        """
        if client or admin:
            return [
                {
                    "title": ButtonLabels.DELETE, # do not change
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
                    "title": ButtonLabels.CLONE,
                    "icon": IconType.ReplayIcon,
                    "action": {
                        "type": "request",
                        "data": { "type": "cloneProcess" },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "project",
                }
            ] 
        else:
            return []
    
    ###################################################
    # Transitions

    ###################################################
    updateTransitions = []
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface,process) # do not change
        
    ###################################################
    def onButtonEvent(self, event: str, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

# fill dictionary
for subclass in State.__subclasses__():
    instance = subclass()
    stateDict[instance.name] = instance