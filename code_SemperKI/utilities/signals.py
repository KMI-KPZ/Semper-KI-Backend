"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Signals that can be sent to other apps
"""

import django.dispatch
import Generic_Backend.code_General.utilities.signals as GeneralSignals
from ..handlers.public.project import saveProjects, saveProjectsViaWebsocket
from ..connections.content.postgresql.pgProfilesSKI import updateOrgaDetailsSemperKI, updateUserDetailsSemperKI
from ..connections.content.postgresql.pgKnowledgeGraph import Basics

################################################################################################

###########################################################
class SemperKISignalDispatchers():
    """
    Defines signal dispatchers that send signals to other apps
    
    """
    pass
semperKISignalDispatcher = SemperKISignalDispatchers()

###########################################################
class SemperKISignalReceivers():
    """
    Defines signal receivers from other apps
    
    """

    ###########################################################
    @staticmethod
    def receiverForLogin(sender, **kwargs):
        """
        If a user logged in, what shall be done?

        """
        saveProjects(request=kwargs["request"])

    ###########################################################
    @staticmethod
    def receiverForLogout(sender, **kwargs):
        """
        If a user logged out, what shall be done?

        """
        saveProjects(request=kwargs["request"])

    ###########################################################
    @staticmethod
    def receiverForWebsocketConnect(sender, **kwargs):
        """
        If websocket connected, what shall be done?

        """
        saveProjectsViaWebsocket(session=kwargs["session"])


    ###########################################################
    @staticmethod
    def receiverForWebsocketDisconnect(sender, **kwargs):
        """
        If websocket disconnected, what shall be done?

        """
        saveProjectsViaWebsocket(session=kwargs["session"])

    ###########################################################
    @staticmethod
    def receiverForUserDetailsUpdate(sender, **kwargs):
        """
        If a user gets initialized or updated, set the SemperKI specific details
        """
        updateUserDetailsSemperKI(userHashID=kwargs["userID"],session=kwargs["session"])

    ###########################################################
    @staticmethod
    def receiverForOrgaDetailsUpdate(sender, **kwargs):
        """
        If a user gets initialized or updated, set the SemperKI specific details
        """
        updateOrgaDetailsSemperKI(orgaHashID=kwargs["orgaID"])
        Basics.createOrganizationNode(orgaID=kwargs["orgaID"])
    
    ###########################################################
    @staticmethod
    def receiverForOrgaDeleted(sender, **kwargs):
        """
        If an organization is deleted, delete all nodes
        """
        Basics.deleteAllNodesFromOrganization(orgaID=kwargs["orgaID"])
    
    ###########################################################
    @staticmethod
    def receiverForUserDeleted(sender, **kwargs):
        """
        If a user is deleted, do something
        """
        userID = kwargs["userID"]
        pass

    ###########################################################
    def __init__(self) -> None:
        """
        Connect all receivers

        """
        GeneralSignals.signalDispatcher.userLoggedIn.connect(self.receiverForLogin, dispatch_uid="1")
        GeneralSignals.signalDispatcher.userLoggedOut.connect(self.receiverForLogout, dispatch_uid="2")
        GeneralSignals.signalDispatcher.websocketConnected.connect(self.receiverForWebsocketConnect, dispatch_uid="3")
        GeneralSignals.signalDispatcher.websocketDisconnected.connect(self.receiverForWebsocketDisconnect, dispatch_uid="4")
        GeneralSignals.signalDispatcher.userUpdated.connect(self.receiverForUserDetailsUpdate, dispatch_uid="5")
        GeneralSignals.signalDispatcher.orgaUpdated.connect(self.receiverForOrgaDetailsUpdate, dispatch_uid="6")
        GeneralSignals.signalDispatcher.userDeleted.connect(self.receiverForUserDeleted, dispatch_uid="7")
        GeneralSignals.signalDispatcher.orgaDeleted.connect(self.receiverForOrgaDeleted, dispatch_uid="8")

semperKISignalReceiver = SemperKISignalReceivers()
    