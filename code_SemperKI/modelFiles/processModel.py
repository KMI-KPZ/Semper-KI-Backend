"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Model for processes
"""
import json, enum
from django.db import models
from django.contrib.postgres.fields import ArrayField

from .projectModel import Project
from code_General.modelFiles.organizationModel import Organization


###################################################
class ProcessDescription(enum.StrEnum):
    """
    What makes up a process object for creation in the database

    """
    processID = enum.auto()
    project = enum.auto()

    processDetails = enum.auto()
    processStatus = enum.auto()

    serviceDetails = enum.auto()
    serviceStatus = enum.auto()
    serviceType = enum.auto()

    client = enum.auto()
    contractor = enum.auto()

    dependenciesIn = enum.auto()
    dependenciesOut = enum.auto()

    createdWhen = enum.auto()
    updatedWhen = enum.auto()
    accessedWhen = enum.auto()


###################################################
class Process(models.Model):
    """
    Process management class.
    
    :processID: Unique ID for that process, primary key
    :project: Signals django to link that process to a project
    :processDetails: Name of the process and stuff
    :processStatus: How everything is going in general
    :serviceDetails: Details for that service
    :serviceStatus: How everything is going for the service
    :serviceType: Which service it is
    :client: Who started the process
    :contractor: Who gets to handle it
    :dependenciesIn: Which process this one depends on
    :dependenciesOut: Which processes depend on this one
    :createdWhen: Automatically assigned date and time(UTC+0) when the entry is created
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the entry was fetched from the database, automatically set
    """
    ###################################################
    processID = models.CharField(primary_key=True,max_length=513)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="processes")
    
    processDetails = models.JSONField()
    processStatus = models.IntegerField()

    serviceDetails = models.JSONField()
    serviceStatus = models.IntegerField()
    serviceType = models.IntegerField()

    client = models.CharField(max_length=513)
    contractor = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name="asContractor")
    
    dependenciesIn = models.ManyToManyField("self", symmetrical=False, related_name="processesIn")
    dependenciesOut = models.ManyToManyField("self", symmetrical=False, related_name="processesOut")
    
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)
    ###################################################
    def __str__(self):
        return ""
    
    def toDict(self):
        return {ProcessDescription.processID: self.processID, 
                ProcessDescription.project: json.dumps(self.project.toDict()), 
                ProcessDescription.serviceDetails: json.dumps(self.serviceDetails), 
                ProcessDescription.processStatus: self.processStatus,
                ProcessDescription.serviceType: self.serviceType,
                ProcessDescription.serviceStatus: self.serviceStatus,
                ProcessDescription.processDetails: json.dumps(self.processDetails),
                ProcessDescription.client: self.client,
                ProcessDescription.contractor: self.contractor.name,
                ProcessDescription.createdWhen: self.createdWhen, ProcessDescription.updatedWhen: self.updatedWhen, ProcessDescription.accessedWhen: self.accessedWhen}
    
