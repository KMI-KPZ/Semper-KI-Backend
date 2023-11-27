"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Model for projects
"""
import json, enum
from django.db import models
from django.contrib.postgres.fields import ArrayField

from code_General.utilities.customStrEnum import StrEnumExactylAsDefined

###################################################
class ProjectDescription(StrEnumExactylAsDefined):
    """
    What does a project consists of?

    """
    projectID = enum.auto()
    status = enum.auto()
    client = enum.auto()
    details = enum.auto()
    createdWhen = enum.auto()
    updatedWhen = enum.auto()
    accessedWhen = enum.auto()


###################################################
class Project(models.Model):
    """
    Project class.
    
    :projectID: Unique ID for that project, primary key
    :status: Current state of the project
    :createdWhen: Automatically assigned date and time(UTC+0) when the entry is created
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the data was fetched from the database, automatically set
    """
    projectID = models.CharField(primary_key=True,max_length=513)
    status = models.IntegerField()
    client = models.CharField(max_length=513)
    details = models.JSONField()
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

    def toDict(self):
        return {ProjectDescription.projectID: self.projectID, ProjectDescription.status: self.status, ProjectDescription.client: self.client, ProjectDescription.details: json.dumps(self.details), ProjectDescription.createdWhen: self.createdWhen, ProjectDescription.updatedWhen: self.updatedWhen, ProjectDescription.accessedWhen: self.accessedWhen }

