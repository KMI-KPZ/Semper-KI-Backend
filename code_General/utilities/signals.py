"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Signals that can be sent to other apps
"""

import django.dispatch

################################################################################################

###########################################################
class SignalDispatchers():
    """
    Defines signal dispatchers that send signals to other apps
    
    """
    userLoggedIn = django.dispatch.Signal()
    userLoggedOut = django.dispatch.Signal()
    websocketConnected = django.dispatch.Signal()
    websocketDisconnected = django.dispatch.Signal()

signalDispatcher = SignalDispatchers()

###########################################################
class SignalReceivers():
    """
    Defines signal receivers from other apps
    
    """
    pass

signalReceiver = SignalReceivers()