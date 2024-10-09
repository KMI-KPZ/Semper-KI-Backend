"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Models for data
"""

import json, enum
from django.db import models
from django.contrib.postgres.fields import ArrayField

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

from .processModel import Process

###################################################
class DataDescription(StrEnumExactlyAsDefined):
    """
    What does a data entry consists of?

    """
    dataID = enum.auto()
    process = enum.auto()
    processID = enum.auto() # interface only
    
    type = enum.auto()
    data = enum.auto()
    details = enum.auto()
    createdBy = enum.auto()
    contentID = enum.auto()

    createdWhen = enum.auto()
    updatedWhen = enum.auto()
    accessedWhen = enum.auto()



###################################################
class Data(models.Model):
    """
    Data management class.
    
    :dataID: Primary Key with hash
    :process: Link to the process that created this entry
    :type: Type of data, defined in another enum
    :data: The data itself
    :details: Meta data and other information
    :createdBy: Who created this data
    :contentID: ID of a file for example, makes searching easier
    :createdWhen: Automatically assigned date and time(UTC+0) when the entry is created
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the data was fetched from the database, automatically set
    """
    ###################################################
    dataID = models.CharField(primary_key=True,max_length=513)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="data")
    
    type = models.IntegerField()
    data = models.JSONField()
    details = models.JSONField()
    createdBy = models.CharField(max_length=513)
    contentID = models.CharField(max_length=513)

    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

    ###################################################
    class Meta:
        ordering = ["createdWhen"]
        indexes = [
            models.Index(fields=["process"], name="process_idx"),
            models.Index(fields=["process","type"], name="process_dataType_idx"),
            models.Index(fields=["process","contentID"], name="process_dataID_idx")
        ]
    ###################################################
    def __str__(self):
        return f"{self.dataID},{self.process},{self.type},{self.data},{self.details},{self.createdBy},{self.createdWhen},{self.updatedWhen},{self.accessedWhen}"
    
    def toDict(self):
        return {DataDescription.dataID: self.dataID, 
                #DataDescription.process: self.process.toDict(), 
                DataDescription.type: self.type, 
                DataDescription.data: self.data,
                DataDescription.details: self.details, 
                DataDescription.createdBy: self.createdBy,
                DataDescription.contentID: self.contentID,
                DataDescription.createdWhen: str(self.createdWhen), DataDescription.updatedWhen: str(self.updatedWhen), DataDescription.accessedWhen: str(self.accessedWhen)}
    
##################################################
class DataInterface():
    """
    Data management class as an interface
    
    :dataID: Primary Key with hash
    :processID: Link to the process that created this entry
    :type: Type of data, defined in another enum
    :data: The data itself
    :details: Meta data and other information
    :createdBy: Who created this data
    :contentID: ID of a file for example, makes searching easier
    :createdWhen: Automatically assigned date and time(UTC+0) when the entry is created
    """

    ##################################################
    def __init__(self, dataID, processID, type, data, details, createdBy, contentID, createdWhen) -> None:
        self.dataID:str = dataID
        self.processID:str = processID
        
        self.type:int = type
        self.data:dict = data
        self.details:dict = details
        self.createdBy:str = createdBy
        self.contentID:str = contentID

        self.createdWhen:str = createdWhen

    ##################################################
    def toDict(self):
        return {DataDescription.dataID: self.dataID, 
                DataDescription.processID: self.processID, 
                DataDescription.type: self.type, 
                DataDescription.data: self.data,
                DataDescription.details: self.details, 
                DataDescription.createdBy: self.createdBy,
                DataDescription.contentID: self.contentID,
                DataDescription.createdWhen: str(self.createdWhen)}
    