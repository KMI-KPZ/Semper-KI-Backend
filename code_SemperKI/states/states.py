from __future__ import annotations 
"""
Part of Semper-KI software

Silvio Weging 2024

Contains: State machine with states
"""


import copy
import logging

from abc import ABC, abstractmethod

from Generic_Backend.code_General.definitions import Logging, UserNotificationTargets
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase, ProfileManagementOrganization, ProfileManagementUser, profileManagement, SessionContent
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists

import code_SemperKI.utilities.websocket as WebsocketEvents
import code_SemperKI.connections.content.session as SessionInterface
import code_SemperKI.connections.content.postgresql.pgProcesses as DBInterface
import code_SemperKI.modelFiles.processModel as ProcessModel
import code_SemperKI.serviceManager as ServiceManager
import code_SemperKI.tasks.processTasks as ProcessTasks
import code_SemperKI.utilities.locales as Locales

from .stateDescriptions import *

from ..definitions import ProcessDescription, ProcessUpdates, SessionContentSemperKI, ProcessDetails, FlatProcessStatus, NotificationSettingsOrgaSemperKI, NotificationSettingsUserSemperKI

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")


###############################################################################
# Functions
#######################################################
def getButtonsForProcess(process:ProcessModel.Process|ProcessModel.ProcessInterface, client=True, admin=False) -> None: #is changed in place
    """
    Look at process status of every process of a project and add respective buttons

    :param process: The current process in question
    :type process: ProcessModel.Process|ProcessModel.ProcessInterface
    :param client: Whether the current user is the client or the contractor
    :type client: Bool
    :param admin: Whether the current user is an admin (which may see all buttons) or not
    :type admin: Bool
    :return: The buttons corresponding to the status
    :rtype: Dict

    """

    processStatusAsString = processStatusFromIntToStr(process.processStatus)
    return stateDict[processStatusAsString].buttons(process, client, admin)

#######################################################
def getFlatStatus(processStatusCode:int, client=True) -> str:
    """
    Get code string if something is required from the user for that status

    :param processStatusCode: The current status of the process
    :type processStatusCode: int
    :param client: Signals, if the user is the client of the process or not
    :type client: Bool
    :returns: The flat status string from FlatProcessStatus
    :rtype: str
    
    """
    processStatusAsString = processStatusFromIntToStr(processStatusCode)
    return stateDict[processStatusAsString].getFlatStatus(client)


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
    :param currentClient: Who is ordering that?
    :type currentClient: str
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
        :param currentClient: Who is ordering that update?
        :type currentClient: str
        :return: Nothing
        :rtype: None
        """

        # The next state will be the result of the onEvent function.
        self.state = self.state.onUpdateEvent(interface, process)
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
        :param currentClient: Who is ordering that update?
        :type currentClient: str
        :return: Nothing
        :rtype: None

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
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Which buttons should be shown in this state
        """
        pass

    ###################################################
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
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
            currentClient = interface.getUserID()
            returnState = self
            for t in self.updateTransitions:
                resultOfTransition = t(self, interface, process)
                if resultOfTransition != self:
                    returnState = resultOfTransition
                    interface.updateProcess(process.project.projectID, process.processID, ProcessUpdates.processStatus, returnState.statusCode, currentClient)

                    notificationPreferences = ProfileManagementBase.getNotificationPreferences(currentClient)
                    sendNotification = False
                    if notificationPreferences is not None:
                        if NotificationSettingsUserSemperKI.statusChange in notificationPreferences and notificationPreferences[NotificationSettingsUserSemperKI.statusChange][UserNotificationTargets.event] == True:
                            sendNotification = True # client whishes to be informed
                    WebsocketEvents.fireWebsocketEvents(process.project.projectID, [process.processID], interface.getSession(), ProcessUpdates.processStatus, "", sendNotification)
                    break # Ensure that only one transition is possible 
            
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
            currentClient = interface.getUserID()
            returnState = self
            for t in self.buttonTransitions:
                if event == t:
                    returnState = self.buttonTransitions[t](self, interface, process)
                    interface.updateProcess(process.project.projectID, process.processID, ProcessUpdates.processStatus, returnState.statusCode, currentClient)
                    
                    notificationPreferences = ProfileManagementBase.getNotificationPreferences(currentClient)
                    sendNotification = False
                    if notificationPreferences is not None:
                        if NotificationSettingsUserSemperKI.statusChange in notificationPreferences and notificationPreferences[NotificationSettingsUserSemperKI.statusChange][UserNotificationTargets.event] == True:
                            sendNotification = True # client whishes to be informed
                    WebsocketEvents.fireWebsocketEvents(process.project.projectID, [process.processID], interface.getSession(), ProcessUpdates.processStatus, "", sendNotification)
                    break # Ensure that only one transition is possible 
            
            return returnState
        except (Exception) as error:
            loggerError.error(f"{self.__str__} {self.onButtonEvent.__name__}: {str(error)}")
            return self

    ###################################################
    def sendMailToClient(self, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface, locale:str, notificationType:str, reason:str, message:str):
        """
        Send a mail to the client

        :param interface: The session or database interface
        :type interface: ProcessManagementSession | ProcessManagementBase
        :param process: The process object
        :type process: Process | ProcessInterface
        :param locale: The locale string for that user
        :type locale: str
        :param notificationType: What type of notification is given here?
        :type notificationType: str
        :param reason: What is the reason for the mail
        :type reason: str
        :param message: The content of the message
        :type message: str
        :return: Nothing
        :rtype: None
        
        """
        # Send mail to client if so desired
        notificationPreferences = ProfileManagementBase.getNotificationPreferences(process.client)
        clientMail = ProfileManagementBase.getEMailAddress(process.client)

        if notificationPreferences is not None:
            if notificationType in notificationPreferences and notificationPreferences[notificationType][UserNotificationTargets.email] == False:
                return # client whishes no email for that
        clientName = ProfileManagementBase.getUserNameViaHash(process.client)
        processTitle = process.processDetails[ProcessDetails.title] if ProcessDetails.title in process.processDetails else process.processID
        ProcessTasks.sendEMail(clientMail, f"{reason} '{processTitle}'", clientName, locale, message)
        
    ###################################################
    def sendMailToContractor(self, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface, locale:str, notificationType:str, reason:str, message:str):
        """
        Send a mail to the contractor

        :param interface: The session or database interface
        :type interface: ProcessManagementSession | ProcessManagementBase
        :param process: The process object
        :type process: Process | ProcessInterface
        :param locale: The locale string for that user
        :type locale: str
        :param notificationType: What type of notification is given here?
        :type notificationType: str
        :param reason: What is the reason for the mail
        :type reason: str
        :param message: The content of the message
        :type message: str
        :return: Nothing
        :rtype: None
        
        """
        # Send mail to contractor
        notificationPreferences = ProfileManagementOrganization.getNotificationPreferences(process.contractor.hashedID)
        if notificationPreferences is not None:
            if notificationType in notificationPreferences and notificationPreferences[notificationType][UserNotificationTargets.email] == False:
                return # contractor whishes no email for that
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
    def buttons(self, process, client=True, admin=False) -> list:
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.ACTION_REQUIRED

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
        return super().onUpdateEvent(interface, process)
    
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process)
    
#######################################################
class SERVICE_IN_PROGRESS(State):
    """
    The service is being edited
    
    """
    
    statusCode = processStatusAsInt(ProcessStatusAsString.SERVICE_IN_PROGRESS)
    name = ProcessStatusAsString.SERVICE_IN_PROGRESS
    
    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Back to draft

        """
        return [
            {
                "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.DRAFT,
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
                "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.SERVICE_COMPLETED,
                "icon": IconType.FactoryIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "forwardStatus",
                        "targetStatus": ProcessStatusAsString.SERVICE_COMPLETED,
                    },
                },
                "active": False,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "both",
            }
        ]
    
    ###################################################
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
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
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process)

#######################################################
class SERVICE_READY(State):
    """
    Service is ready
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.SERVICE_READY)
    name = ProcessStatusAsString.SERVICE_READY

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Finish this service and go to overview

        """
        return [
            {
                "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.DRAFT,
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
                "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.SERVICE_COMPLETED,
                "icon": IconType.FactoryIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "forwardStatus",
                        "targetStatus": ProcessStatusAsString.SERVICE_COMPLETED,
                    },
                },
                "active": True,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "both",
            }
        ] 
    
    ###################################################
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
    ###################################################
    # Transitions
    ##################################################
    def to_SERVICE_IN_PROGRESS(self, interface: SessionInterface.ProcessManagementSession  | DBInterface.ProcessManagementBase, process: ProcessModel.Process  | ProcessModel.ProcessInterface)  -> \
        SERVICE_IN_PROGRESS:
        """
        Service changed	
        """
        if process.serviceType == ServiceManager.serviceManager.getNone() or not ServiceManager.serviceManager.getService(process.serviceType).serviceReady(process.serviceDetails):
            return stateDict[ProcessStatusAsString.SERVICE_IN_PROGRESS]
        else:
            return self
        
    ###################################################
    def to_SERVICE_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
        SERVICE_COMPLETED:
        """
        Service is completely defined

        """
        return stateDict[ProcessStatusAsString.SERVICE_COMPLETED]
    
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
    updateTransitions = [to_SERVICE_COMPLICATION, to_SERVICE_IN_PROGRESS]
    buttonTransitions = {ProcessStatusAsString.DRAFT: to_DRAFT, ProcessStatusAsString.SERVICE_COMPLETED: to_SERVICE_COMPLETED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process)
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process)

#######################################################
class SERVICE_COMPLETED(State):
    """
    Service is ready and has been declared as completely described
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.SERVICE_COMPLETED)
    name = ProcessStatusAsString.SERVICE_COMPLETED

    ###################################################
    def checkIfButtonIsActive(self, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        """
        Check if all requirements are met for the state to advance

        :param process: The process containing the information
        :type process: ProcessModel.Process | ProcessModel.ProcessInterface
        :return: True if conditions are met, false if not
        :rtype: Bool
        """
        return ProcessDetails.provisionalContractor in process.processDetails and process.processDetails[ProcessDetails.provisionalContractor] != "" \
            and ProcessDetails.clientBillingAddress in process.processDetails and process.processDetails[ProcessDetails.clientBillingAddress] != {} \
            and ProcessDetails.clientDeliverAddress in process.processDetails and process.processDetails[ProcessDetails.clientDeliverAddress] != {}       

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Choose contractor

        """
        buttonsList = [
            {
                "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.SERVICE_READY,
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
                "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.CONTRACTOR_COMPLETED,
                "icon": IconType.DoneAllIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "forwardStatus",
                        "targetStatus": ProcessStatusAsString.CONTRACTOR_COMPLETED,
                    },
                },
                "active": False,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "process",
            },
        ]
        
        if self.checkIfButtonIsActive(process):
            buttonsList[2]["active"] = True #set forward button to active

        return buttonsList
    
    ###################################################
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.ACTION_REQUIRED

    # Transitions
    ###################################################
    def to_CONTRACTOR_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
        SERVICE_READY | CONTRACTOR_COMPLETED:
        """
        Contractor was selected

        """
        if self.checkIfButtonIsActive(process):
            return stateDict[ProcessStatusAsString.CONTRACTOR_COMPLETED]
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
        
    ##################################################
    def to_SERVICE_IN_PROGRESS(self, interface: SessionInterface.ProcessManagementSession  | DBInterface.ProcessManagementBase, process: ProcessModel.Process  | ProcessModel.ProcessInterface)  -> \
        SERVICE_IN_PROGRESS:
        """
        Service changed	
        """
        if process.serviceType == ServiceManager.serviceManager.getNone() or not ServiceManager.serviceManager.getService(process.serviceType).serviceReady(process.serviceDetails):
            return stateDict[ProcessStatusAsString.SERVICE_IN_PROGRESS]
        else:
            return self
    
    ###################################################
    def to_SERVICE_READY_Button(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
        SERVICE_READY:
        """
        Button was pressed, go back

        """
        interface.deleteFromProcess(process.project.projectID, process.processID, ProcessUpdates.processDetails, {ProcessDetails.provisionalContractor: ""}, process.client)
        return stateDict[ProcessStatusAsString.SERVICE_READY]
    
    ###################################################
    updateTransitions = [to_SERVICE_IN_PROGRESS, to_SERVICE_COMPLICATION]
    buttonTransitions = {ProcessStatusAsString.SERVICE_READY: to_SERVICE_READY_Button, ProcessStatusAsString.CONTRACTOR_COMPLETED: to_CONTRACTOR_COMPLETED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process)
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process)

#######################################################
class WAITING_FOR_OTHER_PROCESS(State):
    """
    Waiting for other preceding Process

    """

    statusCode = processStatusAsInt(ProcessStatusAsString.WAITING_FOR_OTHER_PROCESS)
    name = ProcessStatusAsString.WAITING_FOR_OTHER_PROCESS

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Buttons for WAITING_FOR_OTHER_PROCESS

        """
        return [
            {
                "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.DRAFT,
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.WAITING_PROCESS
        else:
            return FlatProcessStatus.WAITING_PROCESS
    
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
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class SERVICE_COMPLICATION(State):
    """
    Service Complication happened

    """

    statusCode = processStatusAsInt(ProcessStatusAsString.SERVICE_COMPLICATION)
    name = ProcessStatusAsString.SERVICE_COMPLICATION

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
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
                "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.SERVICE_IN_PROGRESS,
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
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
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class CONTRACTOR_COMPLETED(State):
    """
    Contractor has been chosen (opens page for verification in frontend)
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.CONTRACTOR_COMPLETED)
    name = ProcessStatusAsString.CONTRACTOR_COMPLETED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Buttons for  CONTRACTOR_COMPLETED 

        """
        return [
            {
                "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.SERVICE_COMPLETED,
                "icon": IconType.ArrowBackIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "backstepStatus",
                        "targetStatus": ProcessStatusAsString.SERVICE_COMPLETED,
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
                "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.VERIFYING,
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
    ###################################################
    # Transitions
    ###################################################
    def to_VERIFYING(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          VERIFYING: 
        """
        Starts verification
        From: CONTRACTOR_COMPLETED
        To: VERIFYING

        """
        interface.verifyProcess(process, interface.getSession() , interface.getUserID())
        return stateDict[ProcessStatusAsString.VERIFYING]

    ###################################################
    def to_SERVICE_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          SERVICE_COMPLETED:
        """
        To: SERVICE_COMPLETED
        
        """
        return stateDict[ProcessStatusAsString.SERVICE_COMPLETED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.SERVICE_COMPLETED: to_SERVICE_COMPLETED, ProcessStatusAsString.VERIFYING: to_VERIFYING}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class VERIFYING(State):
    """
    Process is currently being verified

    """

    statusCode = processStatusAsInt(ProcessStatusAsString.VERIFYING)
    name = ProcessStatusAsString.VERIFYING

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Buttons for VERIFYING

        """
        return [
            {
                "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.CONTRACTOR_COMPLETED,
                "icon": IconType.ArrowBackIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "backstepStatus",
                        "targetStatus": ProcessStatusAsString.CONTRACTOR_COMPLETED,
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
            { # this button shall not do anything
                "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.VERIFICATION_COMPLETED,
                "icon": IconType.MailIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "forwardStatus",
                        "targetStatus": ProcessStatusAsString.VERIFYING,
                    },
                },
                "active": False,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "both",
            }
        ] 
    
    ###################################################
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.WAITING_PROCESS
        else:
            return FlatProcessStatus.WAITING_PROCESS
    
    ###################################################
    # Transitions
    ###################################################
    def to_VERIFICATION_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          VERIFYING | VERIFICATION_COMPLETED:
        """
        From: VERIFYING
        To: VERIFICATION_COMPLETED

        """
        # TODO Can only be set by admins (admins need to see buttons)

        return stateDict[ProcessStatusAsString.VERIFICATION_COMPLETED]

    ###################################################
    def to_CONTRACTOR_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CONTRACTOR_COMPLETED:
        """
        To: CONTRACTOR_COMPLETED
        
        """
        return stateDict[ProcessStatusAsString.CONTRACTOR_COMPLETED]

    ###################################################
    updateTransitions = [to_VERIFICATION_COMPLETED]
    buttonTransitions = {ProcessStatusAsString.CONTRACTOR_COMPLETED: to_CONTRACTOR_COMPLETED }

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class VERIFICATION_COMPLETED(State):
    """
    Process has been verified
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.VERIFICATION_COMPLETED)
    name = ProcessStatusAsString.VERIFICATION_COMPLETED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Manual Request

        """
        return [
            {
                "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.CONTRACTOR_COMPLETED,
                "icon": IconType.ArrowBackIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "backstepStatus",
                        "targetStatus": ProcessStatusAsString.CONTRACTOR_COMPLETED,
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
                "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.REQUEST_COMPLETED,
                "icon": IconType.MailIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "forwardStatus",
                        "targetStatus": ProcessStatusAsString.REQUEST_COMPLETED,
                    },
                },
                "active": True,
                "buttonVariant": ButtonTypes.primary,
                "showIn": "both",
            }
        ] 
    
    ###################################################
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
    ###################################################
    # Transitions
    ###################################################
    def to_REQUEST_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          VERIFICATION_COMPLETED | REQUEST_COMPLETED:
        """
        From: VERIFICATION_COMPLETED
        To: REQUEST_COMPLETED

        Is called from the outside by a finished verification
        """
        retVal = interface.sendProcess(process, interface.getSession() , interface.getUserID())
        if isinstance(retVal, Exception):
            return stateDict[ProcessStatusAsString.VERIFICATION_COMPLETED]
        return stateDict[ProcessStatusAsString.REQUEST_COMPLETED]

    ###################################################
    def to_CONTRACTOR_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CONTRACTOR_COMPLETED:
        """
        To: CONTRACTOR_COMPLETED
        
        """
        # TODO discard verification
        return stateDict[ProcessStatusAsString.CONTRACTOR_COMPLETED]

    ###################################################
    updateTransitions = [to_REQUEST_COMPLETED]
    buttonTransitions = {ProcessStatusAsString.CONTRACTOR_COMPLETED: to_CONTRACTOR_COMPLETED, ProcessStatusAsString.REQUEST_COMPLETED: to_REQUEST_COMPLETED} # TODO add functions that are called on button click, leave empty if none exist

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class REQUEST_COMPLETED(State):
    """
    Contractor was informed about possible contract
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.REQUEST_COMPLETED)
    name = ProcessStatusAsString.REQUEST_COMPLETED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Buttons for REQUEST_COMPLETED, no Back-Button, Contractor chooses between Confirm, Reject and Clarification
        
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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.OFFER_COMPLETED,
                    "icon": IconType.DoneAllIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.OFFER_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.OFFER_REJECTED,
                    "icon": IconType.CancelIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.OFFER_REJECTED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                }
            ])
        return outArr
    
    ###################################################
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.WAITING_CONTRACTOR
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
    ###################################################
    # Transitions
    ###################################################
    def to_OFFER_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          REQUEST_COMPLETED | OFFER_COMPLETED:
        """
        From: REQUEST_COMPLETED
        To: OFFER_COMPLETED

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","confirmedByContractor"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","confirmedByContractor"])
        self.sendMailToClient(interface, process, userLocale, NotificationSettingsUserSemperKI.responseFromContractor, subject, message)
        return stateDict[ProcessStatusAsString.OFFER_COMPLETED]

    ###################################################
    def to_OFFER_REJECTED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          REQUEST_COMPLETED | OFFER_REJECTED:
        """
        From: REQUEST_COMPLETED
        To: OFFER_REJECTED

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","declinedByContractor"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","declinedByContractor"])
        self.sendMailToClient(interface, process, userLocale, NotificationSettingsUserSemperKI.responseFromContractor, subject, message)
        return stateDict[ProcessStatusAsString.OFFER_REJECTED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.OFFER_COMPLETED: to_OFFER_COMPLETED, ProcessStatusAsString.OFFER_REJECTED: to_OFFER_REJECTED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

# #######################################################
# class CLARIFICATION(State):
#     """
#     Clarification needed by Contractor

#     """

#     statusCode = processStatusAsInt(ProcessStatusAsString.CLARIFICATION)
#     name = ProcessStatusAsString.CLARIFICATION

#     ###################################################
#     def buttons(self, process, client=True, admin=False) -> list:
#         """
#         Buttons for CLARIFICATION

#         """
#         outArr = []
#         if client or admin:
#             outArr.extend([
#                 {
#                     "title": ButtonLabels.DELETE, # do not change
#                     "icon": IconType.DeleteIcon,
#                     "action": {
#                         "type": "request",
#                         "data": { "type": "deleteProcess" },
#                     },
#                     "active": True,
#                     "buttonVariant": ButtonTypes.primary,
#                     "showIn": "project",
#                 },
#             ])
#         if not client or admin:
#             outArr.extend([
#                 {
#                     "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.OFFER_COMPLETED,
#                     "icon": IconType.DoneAllIcon,
#                     "action": {
#                         "type": "request",
#                         "data": {
#                             "type": "forwardStatus",
#                             "targetStatus": ProcessStatusAsString.OFFER_COMPLETED,
#                         },
#                     },
#                     "active": True,
#                     "buttonVariant": ButtonTypes.primary,
#                     "showIn": "both",
#                 },
#                 {
#                     "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.OFFER_REJECTED,
#                     "icon": IconType.CancelIcon,
#                     "action": {
#                         "type": "request",
#                         "data": {
#                             "type": "forwardStatus",
#                             "targetStatus": ProcessStatusAsString.OFFER_REJECTED,
#                         },
#                     },
#                     "active": True,
#                     "buttonVariant": ButtonTypes.primary,
#                     "showIn": "both",
#                 }
#             ])
#         return outArr
    
#     ###################################################
#     def getFlatStatus(self, client:bool) -> str:
#         """
#         Get code string if something is required from the user for that status

#         :param client: Signals, if the user is the client of the process or not
#         :type client: Bool
#         :returns: The flat status string from FlatProcessStatus
#         :rtype: str
#         """
#         if client:
#             return FlatProcessStatus.ACTION_REQUIRED
#         else:
#             return FlatProcessStatus.WAITING_CLIENT
    
#     ###################################################
#     # Transitions
#     ###################################################
#     def to_OFFER_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
#           CLARIFICATION | OFFER_COMPLETED:
#         """
#         From: CLARIFICATION
#         To: OFFER_COMPLETED

#         """
#         userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
#         subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","confirmedByContractor"])
#         message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","confirmedByContractor"])
#         self.sendMailToClient(interface, process, userLocale, subject, message)
#         return stateDict[ProcessStatusAsString.OFFER_COMPLETED]

#     ###################################################
#     def to_OFFER_REJECTED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
#           CLARIFICATION | OFFER_REJECTED:
#         """
#         From: CLARIFICATION
#         To: OFFER_REJECTED

#         """
#         userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
#         subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","declinedByContractor"])
#         message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","declinedByContractor"])
#         self.sendMailToClient(interface, process, userLocale, subject, message)
#         return stateDict[ProcessStatusAsString.OFFER_REJECTED]

#     ###################################################
#     updateTransitions = [] # TODO add functions that are called on update, leave empty if none exist
#     buttonTransitions = {ProcessStatusAsString.OFFER_COMPLETED: to_OFFER_COMPLETED, ProcessStatusAsString.OFFER_REJECTED: to_OFFER_REJECTED} # TODO add functions that are called on button click, leave empty if none exist

#     ###################################################
#     def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
#         return super().onUpdateEvent(interface, process) # do not change
        
#     ###################################################
#     def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
#         return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class OFFER_COMPLETED(State):
    """
    Order Confirmed by Contractor
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.OFFER_COMPLETED)
    name = ProcessStatusAsString.OFFER_COMPLETED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Buttons for OFFER_COMPLETED, no Back-Button

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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.CONFIRMATION_COMPLETED,
                    "icon": IconType.DoneAllIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.CONFIRMATION_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.CONFIRMATION_REJECTED,
                    "icon": IconType.CancelIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.CONFIRMATION_REJECTED,
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.WAITING_CLIENT

    ###################################################
    # Transitions
    ###################################################
    def to_CONFIRMATION_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          OFFER_COMPLETED | CONFIRMATION_COMPLETED:
        """
        From: OFFER_COMPLETED
        To: CONFIRMATION_COMPLETED

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.contractor.hashedID)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","confirmedByClient"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","confirmedByClient"])
        self.sendMailToContractor(interface, process, userLocale, NotificationSettingsOrgaSemperKI.responseFromClient, subject, message)
        return stateDict[ProcessStatusAsString.CONFIRMATION_COMPLETED]

    ###################################################
    def to_CONFIRMATION_REJECTED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          OFFER_COMPLETED | CONFIRMATION_REJECTED:
        """
        From: OFFER_COMPLETED
        To: CONFIRMATION_REJECTED

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.contractor.hashedID)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","declinedByClient"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","declinedByClient"])
        self.sendMailToContractor(interface, process, userLocale, NotificationSettingsOrgaSemperKI.responseFromClient, subject, message)
        return stateDict[ProcessStatusAsString.CONFIRMATION_REJECTED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.CONFIRMATION_COMPLETED: to_CONFIRMATION_COMPLETED, ProcessStatusAsString.CONFIRMATION_REJECTED: to_CONFIRMATION_REJECTED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class OFFER_REJECTED(State):
    """
    Order Rejected by Contractor
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.OFFER_REJECTED)
    name = ProcessStatusAsString.OFFER_REJECTED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.COMPLETED
    
    ###################################################
    # Transitions
    ###################################################
    def to_CANCELED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          OFFER_REJECTED | CANCELED:
        """
        From: OFFER_REJECTED
        To: CANCELED

        """
        # TODO do stuff to clean up
        return stateDict[ProcessStatusAsString.CANCELED]

    ###################################################
    updateTransitions = [to_CANCELED]
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class CONFIRMATION_COMPLETED(State):
    """
    Order Confirmed by Client
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.CONFIRMATION_COMPLETED)
    name = ProcessStatusAsString.CONFIRMATION_COMPLETED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Buttons for CONFIRMATION_COMPLETED, no Back-Button

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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.PRODUCTION_IN_PROGRESS,
                    "icon": IconType.FactoryIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.PRODUCTION_IN_PROGRESS,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                }
            ] )
        return outArr
    
    ###################################################
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.WAITING_CONTRACTOR
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
    ###################################################
    # Transitions
    ###################################################
    def to_PRODUCTION_IN_PROGRESS(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CONFIRMATION_COMPLETED | PRODUCTION_IN_PROGRESS:
        """
        From: CONFIRMATION_COMPLETED
        To: PRODUCTION_IN_PROGRESS

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","inProduction"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","inProduction"])
        self.sendMailToClient(interface, process, userLocale, NotificationSettingsUserSemperKI.statusChange, subject, message)
        return stateDict[ProcessStatusAsString.PRODUCTION_IN_PROGRESS]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.PRODUCTION_IN_PROGRESS: to_PRODUCTION_IN_PROGRESS}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class CONFIRMATION_REJECTED(State):
    """
    Order rejected by Client
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.CONFIRMATION_REJECTED)
    name = ProcessStatusAsString.CONFIRMATION_REJECTED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.COMPLETED
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
    ###################################################
    # Transitions
    ###################################################
    def to_CANCELED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          CONFIRMATION_REJECTED | CANCELED:
        """
        From: CONFIRMATION_REJECTED
        To: CANCELLED

        """
        # TODO clean up and stuff
        return stateDict[ProcessStatusAsString.CANCELED]

    ###################################################
    updateTransitions = [to_CANCELED]
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class PRODUCTION_IN_PROGRESS(State):
    """
    Order is in Production
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.PRODUCTION_IN_PROGRESS)
    name = ProcessStatusAsString.PRODUCTION_IN_PROGRESS

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Buttons for PRODUCTION_IN_PROGRESS, no Back-Button

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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.PRODUCTION_COMPLETED,
                    "icon": IconType.LocalShippingIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.PRODUCTION_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.FAILED,
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.WAITING_CONTRACTOR
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
    ###################################################
    # Transitions
    ###################################################
    def to_PRODUCTION_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          PRODUCTION_IN_PROGRESS | PRODUCTION_COMPLETED:
        """
        From: PRODUCTION_IN_PROGRESS
        To: DELIVERY_IN_PROGRESS

        """
        return stateDict[ProcessStatusAsString.PRODUCTION_COMPLETED]

    ###################################################
    def to_FAILED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          PRODUCTION_IN_PROGRESS | FAILED:
        """
        From: PRODUCTION_IN_PROGRESS
        To: FAILED

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","productionFailed"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","productionFailed"])
        self.sendMailToClient(interface, process, userLocale, NotificationSettingsUserSemperKI.statusChange, subject, message)
        return stateDict[ProcessStatusAsString.FAILED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.PRODUCTION_COMPLETED: to_PRODUCTION_COMPLETED, ProcessStatusAsString.FAILED: to_FAILED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class PRODUCTION_COMPLETED(State):
    """
    Order is in Production
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.PRODUCTION_COMPLETED)
    name = ProcessStatusAsString.PRODUCTION_COMPLETED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Buttons for PRODUCTION_COMPLETED, no Back-Button

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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.DELIVERY_IN_PROGRESS,
                    "icon": IconType.LocalShippingIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.DELIVERY_IN_PROGRESS,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": "both",
                },
                {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.FAILED,
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.WAITING_CONTRACTOR
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
    ###################################################
    # Transitions
    ###################################################
    def to_DELIVERY_IN_PROGRESS(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          PRODUCTION_COMPLETED | DELIVERY_IN_PROGRESS:
        """
        From: PRODUCTION_IN_PROGRESS
        To: DELIVERY_IN_PROGRESS

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","inDelivery"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","inDelivery"])
        self.sendMailToClient(interface, process, userLocale, NotificationSettingsUserSemperKI.statusChange, subject, message)
        return stateDict[ProcessStatusAsString.DELIVERY_IN_PROGRESS]

    ###################################################
    def to_FAILED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          PRODUCTION_COMPLETED | FAILED:
        """
        From: PRODUCTION_COMPLETED
        To: FAILED

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","productionFailed"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","productionFailed"])
        self.sendMailToClient(interface, process, userLocale, NotificationSettingsUserSemperKI.statusChange, subject, message)
        return stateDict[ProcessStatusAsString.FAILED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.DELIVERY_IN_PROGRESS: to_DELIVERY_IN_PROGRESS, ProcessStatusAsString.FAILED: to_FAILED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class DELIVERY_IN_PROGRESS(State):
    """
    Order is being delivered
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.DELIVERY_IN_PROGRESS)
    name = ProcessStatusAsString.DELIVERY_IN_PROGRESS

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Buttons for DELIVERY_IN_PROGRESS, no Back-Button

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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.DELIVERY_COMPLETED,
                    "icon": IconType.DoneAllIcon,
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.DELIVERY_COMPLETED,
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.WAITING_CLIENT

    ###################################################
    # Transitions
    ###################################################
    def to_DELIVERY_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DELIVERY_IN_PROGRESS | DELIVERY_COMPLETED:
        """
        From: DELIVERY_IN_PROGRESS
        To: DELIVERY_COMPLETED

        """
        # TODO maybe set from outside
        return stateDict[ProcessStatusAsString.DELIVERY_COMPLETED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.DELIVERY_COMPLETED: to_DELIVERY_COMPLETED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class DELIVERY_COMPLETED(State):
    """
    Order is being delivered
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.DELIVERY_COMPLETED)
    name = ProcessStatusAsString.DELIVERY_COMPLETED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
        """
        Buttons for DELIVERY_COMPLETED, no Back-Button

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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.COMPLETED,
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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.DISPUTE,
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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.FAILED,
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.ACTION_REQUIRED
        else:
            return FlatProcessStatus.WAITING_CLIENT

    ###################################################
    # Transitions
    ###################################################
    def to_COMPLETED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DELIVERY_COMPLETED | COMPLETED:
        """
        From: DELIVERY_COMPLETED
        To: COMPLETED

        """
        
        # signal to dependent processes, that this one is finished
        signalCompleteToDependentProcesses(interface, process)

        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","processFinished"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","processFinished"])
        self.sendMailToContractor(interface, process, userLocale, NotificationSettingsOrgaSemperKI.statusChange, subject, message)
        return stateDict[ProcessStatusAsString.COMPLETED]

    ###################################################
    def to_DISPUTE(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DELIVERY_COMPLETED | DISPUTE:
        """
        From: DELIVERY_COMPLETED
        To: DISPUTE

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","dispute"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","dispute"])
        self.sendMailToContractor(interface, process, userLocale, NotificationSettingsOrgaSemperKI.errorOccurred, subject, message)
        return stateDict[ProcessStatusAsString.DISPUTE]

    ###################################################
    def to_FAILED(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface) -> \
          DELIVERY_COMPLETED | FAILED:
        """
        From: DELIVERY_COMPLETED
        To: FAILED

        """
        userLocale = ProfileManagementBase.getUserLocale(hashedID=process.client)
        subject = Locales.manageTranslations.getTranslation(userLocale, ["email","subjects","failed"])
        message = Locales.manageTranslations.getTranslation(userLocale, ["email","content","failed"])
        self.sendMailToContractor(interface, process, userLocale, NotificationSettingsOrgaSemperKI.errorOccurred, subject, message)
        return stateDict[ProcessStatusAsString.FAILED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.COMPLETED: to_COMPLETED, ProcessStatusAsString.DISPUTE: to_DISPUTE, ProcessStatusAsString.FAILED: to_FAILED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class DISPUTE(State):
    """
    Dispute over Delivery
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.DISPUTE)
    name = ProcessStatusAsString.DISPUTE

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.COMPLETED,
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
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.FAILED,
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.WAITING_CONTRACTOR
        else:
            return FlatProcessStatus.ACTION_REQUIRED
    
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
        self.sendMailToContractor(interface, process, userLocale, NotificationSettingsOrgaSemperKI.statusChange, subject, message)
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
        self.sendMailToContractor(interface, process, userLocale, NotificationSettingsOrgaSemperKI.errorOccurred, subject, message)
        return stateDict[ProcessStatusAsString.FAILED]

    ###################################################
    updateTransitions = []
    buttonTransitions = {ProcessStatusAsString.COMPLETED: to_COMPLETED, ProcessStatusAsString.COMPLETED: to_FAILED}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class COMPLETED(State):
    """
    Order has been completed
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.COMPLETED)
    name = ProcessStatusAsString.COMPLETED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.COMPLETED
        else:
            return FlatProcessStatus.COMPLETED
    
    ###################################################
    # Transitions

    ###################################################
    updateTransitions = []
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class FAILED(State):
    """
    Contractor has failed the contract
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.FAILED)
    name = ProcessStatusAsString.FAILED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.COMPLETED
        else:
            return FlatProcessStatus.COMPLETED
    
    ###################################################
    # Transitions

    ###################################################
    updateTransitions = []
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

#######################################################
class CANCELED(State):
    """
    Order has been canceled
    """

    statusCode = processStatusAsInt(ProcessStatusAsString.CANCELED)
    name = ProcessStatusAsString.CANCELED

    ###################################################
    def buttons(self, process, client=True, admin=False) -> list:
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
    def getFlatStatus(self, client:bool) -> str:
        """
        Get code string if something is required from the user for that status

        :param client: Signals, if the user is the client of the process or not
        :type client: Bool
        :returns: The flat status string from FlatProcessStatus
        :rtype: str
        """
        if client:
            return FlatProcessStatus.COMPLETED
        else:
            return FlatProcessStatus.COMPLETED
    
    ###################################################
    # Transitions

    ###################################################
    updateTransitions = []
    buttonTransitions = {}

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        return super().onUpdateEvent(interface, process) # do not change
        
    ###################################################
    def onButtonEvent(self, event:str, interface:SessionInterface.ProcessManagementSession|DBInterface.ProcessManagementBase, process:ProcessModel.Process|ProcessModel.ProcessInterface):
        return super().onButtonEvent(event, interface, process) # do not change

# fill dictionary
for subclass in State.__subclasses__():
    instance = subclass()
    stateDict[instance.name] = instance