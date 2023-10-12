"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Models for projects and processes
"""
import json
from django.db import models
from django.contrib.postgres.fields import ArrayField

###################################################
class Project(models.Model):
    """
    Project class.
    
    :projectID: Unique ID for that project, primary key
    :status: Current state of the project
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    """
    projectID = models.CharField(primary_key=True,max_length=513)
    status = models.IntegerField()
    client = models.CharField(max_length=513)
    details = models.JSONField()
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

    def toDict(self):
        return {"projectID": self.projectID, "status": self.status, "client": self.client, "details": json.dumps(self.details), "created": self.createdWhen, "updated": self.updatedWhen, "accessed": self.accessedWhen }

###################################################
class Process(models.Model):
    """
    Process management class.
    
    :processID: Unique ID for that process, primary key
    :projectKey: Signals django to link that process to a project
    :service: Service and details for that process
    :status: How everything is going in general
    :serviceStatus: How everything is going for the service
    :messages: What was said by whom to whom and when
    :files: All URL Paths of files uploaded for a process
    :client: Who started the process
    :contractor: Who gets to handle it
    :details: Name of the process and stuff
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    """
    ###################################################
    processID = models.CharField(primary_key=True,max_length=513)
    projectKey = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="processes")
    service = models.JSONField()
    status = models.IntegerField()
    serviceStatus = models.IntegerField()
    messages = models.JSONField()
    files = models.JSONField()
    client = models.CharField(max_length=513)
    contractor = ArrayField(models.CharField(max_length=513))
    details = models.JSONField()
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
                "projectKey": str(self.projectKey), 
                "service": json.dumps(self.service), 
                "status": self.status,
                "serviceStatus": self.serviceStatus,
                "messages": json.dumps(self.messages),
                "details": json.dumps(self.details),
                "files": json.dumps(self.files),
                "client": self.client,
                "contractor": self.contractor,
                "created": self.createdWhen, "updated": self.updatedWhen, "accessed": self.accessedWhen}
    
