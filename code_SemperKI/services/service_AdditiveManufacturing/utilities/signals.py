"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Signals send by the other apps which relate to the Additive Manufacturing service
"""

import Generic_Backend.code_General.utilities.signals as GeneralSignals

from ..service import SERVICE_NUMBER
from ..connections.postgresql.pgProfilesSKIAM import updateOrgaDetailsSemperKIAM, deleteOrgaDetailsSemperKIAM

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
        selectedServices = kwargs["details"]
        orgaID = kwargs["orgaID"]
        for service in selectedServices:
            if service == SERVICE_NUMBER:
                updateOrgaDetailsSemperKIAM(orgaID)

    ##################################################
    @staticmethod
    def receiverForOrgaServiceDeletion(sender, **kwargs):
        """
        If an organization deletes a service, what shall be done?

        """
        selectedServices = kwargs["details"]
        orgaID = kwargs["orgaID"]
        for service in selectedServices:
            if service == SERVICE_NUMBER:
                deleteOrgaDetailsSemperKIAM(orgaID)

    ##################################################
    def __init__(self) -> None:
        """
        Connect all receivers

        """
        GeneralSignals.signalDispatcher.orgaServiceDetails.connect(self.receiverForOrgaServiceSelection, dispatch_uid="101")
        GeneralSignals.signalDispatcher.orgaServiceDeletion.connect(self.receiverForOrgaServiceDeletion, dispatch_uid="102")
        
additiveManufacturingSignalReceiver = AdditiveManufacturingSignalReceivers()
