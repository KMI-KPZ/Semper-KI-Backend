"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Model for projects
"""
import json, enum
from django.db import models
from django.contrib.postgres.fields import ArrayField

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

###################################################
class ProjectDescription(StrEnumExactlyAsDefined):
    """
    What does a project consists of?

    """
    projectID = enum.auto()
    projectStatus = enum.auto()
    client = enum.auto()
    projectDetails = enum.auto()
    createdWhen = enum.auto()
    updatedWhen = enum.auto()
    accessedWhen = enum.auto()


###################################################
class Project(models.Model):
    """
    Project class.
    
    :projectID: Unique ID for that project, primary key
    :projectStatus: Current state of the project
    :client: The hashed ID of the client that created the project
    :projectDetails: Details like name and such
    :createdWhen: Automatically assigned date and time(UTC+0) when the entry is created
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the data was fetched from the database, automatically set
    """
    projectID = models.CharField(primary_key=True,max_length=513)
    projectStatus = models.IntegerField()
    client = models.CharField(max_length=513)
    projectDetails = models.JSONField()
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

    def toDict(self):
        return {
            ProjectDescription.projectID: self.projectID,
            ProjectDescription.projectStatus: self.projectStatus,
            ProjectDescription.client: self.client,
            ProjectDescription.projectDetails: self.projectDetails,
            ProjectDescription.createdWhen: str(self.createdWhen),
            ProjectDescription.updatedWhen: str(self.updatedWhen),
            ProjectDescription.accessedWhen: str(self.accessedWhen)
        }


###################################################
class ProjectInterface():
    """
    Project class interface
    
    :projectID: Unique ID for that project, primary key
    :projectStatus: Current state of the project
    :client: The hashed ID of the client that created the project
    :projectDetails: Details like name and such
    :createdWhen: Automatically assigned date and time(UTC+0) when the entry is created
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the data was fetched from the database, automatically set
    """
    projectID = ""
    projectStatus = 0
    client = ""
    projectDetails = {}
    createdWhen = ""
    updatedWhen = ""
    accessedWhen = ""

    ###################################################
    def __init__(self, projectID:str, currentTime:str, client) -> None:
        self.projectID = projectID
        self.projectStatus = 0
        self.client = client
        self.projectDetails = {}
        self.createdWhen = currentTime
        self.updatedWhen = currentTime
        self.accessedWhen = currentTime

    ###################################################
    def setValues(self, projectStatus, client, projectDetails, updatedWhen, accessedWhen) -> None:
        self.projectStatus = projectStatus
        self.client = client
        self.projectDetails = projectDetails
        self.updatedWhen = updatedWhen
        self.accessedWhen = accessedWhen
        
    ###################################################
    def toDict(self):
        return {ProjectDescription.projectID: self.projectID, ProjectDescription.projectStatus: self.projectStatus, ProjectDescription.client: self.client, ProjectDescription.projectDetails: self.projectDetails, ProjectDescription.createdWhen: str(self.createdWhen), ProjectDescription.updatedWhen: str(self.updatedWhen), ProjectDescription.accessedWhen: str(self.accessedWhen) }
