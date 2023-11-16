"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Model for processes
"""
import json
from django.db import models
from django.contrib.postgres.fields import ArrayField

from .projectModel import Project
from .organizationModel import Organization

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
        return {"processID": self.processID, 
                "project": str(self.project), 
                "serviceDetails": json.dumps(self.serviceDetails), 
                "processStatus": self.processStatus,
                "serviceType": self.serviceType,
                "serviceStatus": self.serviceStatus,
                "processDetails": json.dumps(self.processDetails),
                "client": self.client,
                "contractor": self.contractor,
                "created": self.createdWhen, "updated": self.updatedWhen, "accessed": self.accessedWhen}
    
