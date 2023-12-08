"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Signals that can be sent to other apps
"""

import django.dispatch
import code_General.utilities.signals as GeneralSignals
from ..handlers.projectAndProcessManagement import saveProjects, saveProjectsViaWebsocket

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
    def __init__(self) -> None:
        """
        Connect all receivers

        """
        GeneralSignals.signalDispatcher.userLoggedIn.connect(self.receiverForLogin, dispatch_uid="1")
        GeneralSignals.signalDispatcher.userLoggedOut.connect(self.receiverForLogout, dispatch_uid="2")
        GeneralSignals.signalDispatcher.websocketConnected.connect(self.receiverForWebsocketConnect, dispatch_uid="3")
        GeneralSignals.signalDispatcher.websocketDisconnected.connect(self.receiverForWebsocketDisconnect, dispatch_uid="4")

semperKISignalReceiver = SemperKISignalReceivers()
    