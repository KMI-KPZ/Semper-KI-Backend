"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Models for data
"""

import json
from django.db import models
from django.contrib.postgres.fields import ArrayField

from .processModel import Process

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
        return {"dataID": self.dataID, 
                "process": str(self.process), 
                "type": json.dumps(self.type), 
                "data": json.dumps(self.data),
                "details": json.dumps(self.details), 
                "createdBy": self.createdBy,
                "contentID": self.contentID,
                "created": self.createdWhen, "updated": self.updatedWhen, "accessed": self.accessedWhen}
    
