"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Models for events
"""

import enum
from django.db import models

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

##################################################
class EventDescription(StrEnumExactlyAsDefined):
    """
    What does an event entry consists of?
    
    """
    eventID = enum.auto()
    userHashedID = enum.auto()
    event = enum.auto()
    createdWhen = enum.auto()

##################################################
class Event(models.Model):
    """
    Event database class

    :eventID: Primary key
    :userHashedID: ID of the user that is the recipient of the event
    :event: The event itself
    :createdWhen: Automatically assigned date and time(UTC+0) when the entry is created
    
    """
    eventID = models.CharField(primary_key=True, max_length=513)
    userHashedID = models.CharField(max_length=513)
    event = models.JSONField()
    createdWhen = models.DateTimeField(auto_now_add=True)

    ###################################################
    class Meta:
        ordering = ["createdWhen"]
        indexes = [
            models.Index(fields=["userHashedID"], name="event_user_idx")
        ]

    ##################################################
    def __str__(self):
        return f"{self.eventID},{self.userHashedID},{self.event},{self.createdWhen}"
    
    ##################################################
    def toDict(self):
        return {
            EventDescription.eventID: self.eventID,
            EventDescription.userHashedID: self.userHashedID,
            EventDescription.event: self.event,
            EventDescription.createdWhen: str(self.createdWhen)
        }