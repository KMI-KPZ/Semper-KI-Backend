"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Model for database version of the Knowledge Graph
"""

import json, enum
from django.db import models

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

##################################################
class VerificationDescription(StrEnumExactlyAsDefined):
    """
    What does the verification table consists of?

    """
    organizationID = enum.auto()
    printerID = enum.auto()
    materialID = enum.auto()
    status = enum.auto()
    details = enum.auto()
    createdWhen = enum.auto()
    updatedWhen = enum.auto()
    accessedWhen = enum.auto()

##################################################
class VerificationDetails(StrEnumExactlyAsDefined):
    """
    Details of the verification
    
    """
    pass

##################################################
class VerificationStatus(enum.IntEnum):
    """
    Status of the verification
    
    """
    notInitialized = 0
    initialized = 1
    sent = 2
    verified = 3

##################################################
class Verification(models.Model):
    """
    The verification model
    
    """
    organizationID = models.CharField(max_length=512)
    printerID = models.CharField(max_length=512)
    materialID = models.CharField(max_length=512)
    status = models.IntegerField()
    details = models.JSONField()
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField(auto_now=True)
    accessedWhen = models.DateTimeField(auto_now=True)
    
    ###################################################
    class Meta:
        indexes = [
            models.Index(fields=["organizationID"], name="organizationID_idx"),
        ]

    ###################################################
    def __str__(self):
        return self.organizationID + " - " + self.printerID + " - " + self.materialID + " - " + self.status + " - " + json.dumps(self.details) + " - " + str(self.createdWhen) + " - " + str(self.updatedWhen) + " - " + str(self.accessedWhen)
    
    ###################################################
    def toDict(self):
        """
        Dict representation of the verification

        """
        return {
            VerificationDescription.organizationID: self.organizationID,
            VerificationDescription.printerID: self.printerID,
            VerificationDescription.materialID: self.materialID,
            VerificationDescription.status: self.status,
            VerificationDescription.details: self.details,
            VerificationDescription.createdWhen: str(self.createdWhen),
            VerificationDescription.updatedWhen: str(self.updatedWhen),
            VerificationDescription.accessedWhen: str(self.accessedWhen)
        }