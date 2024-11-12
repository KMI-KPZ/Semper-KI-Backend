"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Signals send by the other apps which relate to the Additive Manufacturing service
"""

import Generic_Backend.code_General.utilities.signals as GeneralSignals

################################################################################################

class AdditiveManufacturingSignalReceivers():
    """
    Defines signal receivers from other apps
    
    """
    ##################################################
    @staticmethod
    def receiverForOrgaServiceSelection(sender, **kwargs):
        """
        If an organization selects a service, what shall be done?

        """
        pass

    ##################################################
    def __init__(self) -> None:
        """
        Connect all receivers

        """
        GeneralSignals.signalDispatcher.orgaServiceDetails.connect(self.receiverForOrgaServiceSelection)
        
additiveManufacturingSignalReceiver = AdditiveManufacturingSignalReceivers()