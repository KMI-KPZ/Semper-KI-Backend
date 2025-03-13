"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Buttons for the state machine
"""

from .stateDescriptions import *

#######################################################
# Button definitions
class ButtonDefinitions:
    """
    Define the buttons here and use them in the states
    
    """
    deleteProcess = {
                    "title": ButtonLabels.DELETE_PROCESS,
                    "icon": IconType.DeleteIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": { "type": "deleteProcess" },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    editServiceSelection = {
                    "title": ButtonLabels.EDIT,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "up",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.DRAFT,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.ServiceSelection,
                }
    deleteServiceDetails = {
                    "title": ButtonLabels.DELETE,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "up",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.DRAFT,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.ServiceDetails,
                }
    editServiceDetails = {
                    "title": ButtonLabels.EDIT,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "up",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.SERVICE_IN_PROGRESS,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.ServiceDetails,
                }
    editContractorCompleted = {
                    "title": ButtonLabels.EDIT,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "up",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.SERVICE_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.Contractor,
                }
    deleteContractorCompleted = {
                    "title": ButtonLabels.DELETE,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "up",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.SERVICE_READY,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.Contractor,
                }
    editVerification = {
                    "title": ButtonLabels.EDIT,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "up",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.CONTRACTOR_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.Verification,
                }
    deleteVerification = {
                    "title": ButtonLabels.DELETE,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "up",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.SERVICE_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.Verification,
                }
    backToDraft = {
                    "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.DRAFT,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.DRAFT,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.Active,
                }
    backToServiceReady = {
                    "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.SERVICE_READY,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.SERVICE_READY,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.Active,
                }
    backToServiceCompleted = {
                    "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.SERVICE_COMPLETED,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.SERVICE_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.Active,
                }
    backToContractorCompleted = {
                    "title": ButtonLabels.BACK+"-TO-"+ProcessStatusAsString.CONTRACTOR_COMPLETED,
                    "icon": IconType.ArrowBackIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "backstepStatus",
                            "targetStatus": ProcessStatusAsString.CONTRACTOR_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.secondary,
                    "showIn": ShowIn.Active,
                }
    forwardToServiceCompleted = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.SERVICE_COMPLETED,
                    "icon": IconType.ArrowForwardIcon,
                    "iconPosition": "right",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.SERVICE_COMPLETED,
                        },
                    },
                    "active": False,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    fowardToServiceInProgress = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.SERVICE_IN_PROGRESS,
                    "icon": IconType.ArrowForwardIcon,
                    "iconPosition": "right",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.SERVICE_IN_PROGRESS,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    
    fowardToContractorCompleted = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.CONTRACTOR_COMPLETED,
                    "icon": IconType.ArrowForwardIcon,
                    "iconPosition": "right",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.CONTRACTOR_COMPLETED,
                        },
                    },
                    "active": False,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToVerifying = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.VERIFYING,
                    "icon": IconType.ArrowForwardIcon,
                    "iconPosition": "right",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.VERIFYING,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    fowardToVerificationCompleted = { 
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.VERIFICATION_COMPLETED,
                    "icon": IconType.ArrowForwardIcon,
                    "iconPosition": "right",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.VERIFYING,
                        },
                    },
                    "active": False,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToRequestCompleted = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.REQUEST_COMPLETED,
                    "icon": IconType.ArrowForwardIcon,
                    "iconPosition": "right",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.REQUEST_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToOfferRejected = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.OFFER_REJECTED,
                    "icon": IconType.CancelIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.OFFER_REJECTED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToOfferCompleted = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.OFFER_COMPLETED,
                    "icon": IconType.DoneIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.OFFER_COMPLETED,
                        },
                    },
                    "active": False,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToConfirmationRejected ={
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.CONFIRMATION_REJECTED,
                    "icon": IconType.CancelIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.CONFIRMATION_REJECTED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToConfirmationCompleted = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.CONFIRMATION_COMPLETED,
                    "icon": IconType.DoneIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.CONFIRMATION_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToProductionInProgress = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.PRODUCTION_IN_PROGRESS,
                    "icon": IconType.ArrowForwardIcon,
                    "iconPosition": "right",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.PRODUCTION_IN_PROGRESS,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToFailed = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.FAILED,
                    "icon": IconType.CancelIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.FAILED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardProductionCompleted = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.PRODUCTION_COMPLETED,
                    "icon": IconType.DoneIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.PRODUCTION_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToDeliveryInProgress = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.DELIVERY_IN_PROGRESS,
                    "icon": IconType.LocalShippingIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.DELIVERY_IN_PROGRESS,
                        },
                    },
                    "active": False,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToDeliveryCompleted = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.DELIVERY_COMPLETED,
                    "icon": IconType.ArrowForwardIcon,
                    "iconPosition": "right",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.DELIVERY_COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToDispute = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.DISPUTE,
                    "icon": IconType.QuestionAnswerIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.DISPUTE,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    forwardToCompleted = {
                    "title": ButtonLabels.FORWARD+"-TO-"+ProcessStatusAsString.COMPLETED,
                    "icon": IconType.DoneAllIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": {
                            "type": "forwardStatus",
                            "targetStatus": ProcessStatusAsString.COMPLETED,
                        },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }
    clone = {
                    "title": ButtonLabels.CLONE,
                    "icon": IconType.CloneIcon,
                    "iconPosition": "left",
                    "action": {
                        "type": "request",
                        "data": { "type": "cloneProcesses" },
                    },
                    "active": True,
                    "buttonVariant": ButtonTypes.primary,
                    "showIn": ShowIn.Active,
                }