
import code_SemperKI.utilities.states.stateDescriptions as Descriptions
import code_SemperKI.handlers.projectAndProcessManagement as PPManagement
import code_SemperKI.connections.content.session as SessionInterface
import code_SemperKI.connections.content.postgresql.pgProcesses as DBInterface
import code_SemperKI.modelFiles.processModel as ProcessModel

import logging

from Generic_Backend.code_General.utilities.basics import Logging


from ...connections.content.manageContent import ManageContent
from ...serviceManager import serviceManager
from ...definitions import ProcessDescription, ProcessUpdates

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

###############################################################################
# States
#######################################################
class DRAFT(Descriptions.State):
    """
    The draft state, default
    """

    statusCode = Descriptions.processStatusAsInt(Descriptions.ProcessStatusAsString.DRAFT)

    ###################################################
    def buttons(self) -> list:
        """
        None
        """
        return []
        
    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        try:
            if process.serviceType != serviceManager.getNone():
                interface.updateProcess(process.project.projectID, process.processID, ProcessUpdates.processStatus, Descriptions.processStatusAsInt(Descriptions.ProcessStatusAsString.SERVICE_IN_PROGRESS), process.client)
                return SERVICE_IN_PROGRESS()
            else:
                return self
        except (Exception) as error:
            loggerError.error(f"DRAFT onUpdateEvent: {str(error)}")
            return self
    
    ###################################################
    def onButtonEvent(self, event: str):
        try:
            return self
        except (Exception) as error:
            loggerError.error(f"DRAFT onButtonEvent: {str(error)}")
            return self
    
    
#######################################################
class SERVICE_IN_PROGRESS(Descriptions.State):
    """
    The service is being edited
    
    """
    
    statusCode = Descriptions.processStatusAsInt(Descriptions.ProcessStatusAsString.SERVICE_IN_PROGRESS)
    
    ###################################################
    def buttons(self) -> list:
        """
        Back to draft

        """
        return [
            {
                "title": Descriptions.ButtonLabels.BACK,
                "icon": Descriptions.IconType.ArrowBackIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "backstepStatus",
                        "targetStatus": Descriptions.ProcessStatusAsString.DRAFT,
                    },
                },
                "active": True,
                "buttonVariant": Descriptions.ButtonTypes.secondary,
                "showIn": "process",
            },
            {
                "title": Descriptions.ButtonLabels.DELETE,
                "icon": Descriptions.IconType.DeleteIcon,
                "action": {
                    "type": "request",
                    "data": { "type": "deleteProcess" },
                },
                "active": True,
                "buttonVariant": Descriptions.ButtonTypes.primary,
                "showIn": "project",
            }
        ]

    ###################################################
    def onUpdateEvent(self, interface: SessionInterface.ProcessManagementSession | DBInterface.ProcessManagementBase, process: ProcessModel.Process | ProcessModel.ProcessInterface):
        try:
            if serviceManager.getService(process.serviceType).serviceReady():
                interface.updateProcess(process.project.projectID, process.processID, ProcessUpdates.processStatus, Descriptions.processStatusAsInt(Descriptions.ProcessStatusAsString.SERVICE_READY), process.client)
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
class SERVICE_READY(Descriptions.State):
    """
    Service is ready
    """

    statusCode = Descriptions.processStatusAsInt(Descriptions.ProcessStatusAsString.SERVICE_READY)

    ###################################################
    def buttons(self) -> list:
        """
        Choose contractor

        """
        return [
            {
                "title": Descriptions.ButtonLabels.BACK,
                "icon": Descriptions.IconType.ArrowBackIcon,
                "action": {
                    "type": "request",
                    "data": {
                        "type": "backstepStatus",
                        "targetStatus": Descriptions.ProcessStatusAsString.DRAFT,
                    },
                },
                "active": True,
                "buttonVariant": Descriptions.ButtonTypes.secondary,
                "showIn": "process",
            },
            {
                "title": Descriptions.ButtonLabels.DELETE,
                "icon": Descriptions.IconType.DeleteIcon,
                "action": {
                    "type": "request",
                    "data": { "type": "deleteProcess" },
                },
                "active": True,
                "buttonVariant": Descriptions.ButtonTypes.primary,
                "showIn": "project",
            },
            {
                "title": Descriptions.ButtonLabels.CONTRACTOR_SELECTED,
                "icon": Descriptions.IconType.FactoryIcon,
                "action": {
                    "type": "navigation",
                    "to": Descriptions.ProcessStatusAsString.CONTRACTOR_SELECTED,
                },
                "active": True,
                "buttonVariant": Descriptions.ButtonTypes.primary,
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