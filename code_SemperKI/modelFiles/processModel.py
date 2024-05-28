from __future__ import annotations 
"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Model for processes
"""
import json, enum, copy
from django.db import models
from django.contrib.postgres.fields import ArrayField

from .projectModel import Project, ProjectInterface
from ..serviceManager import serviceManager
from Generic_Backend.code_General.modelFiles.organizationModel import Organization
from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactylAsDefined

###################################################
class ProcessDescription(StrEnumExactylAsDefined):
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

    files = enum.auto()
    messages = enum.auto()

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
    :files: Registrar keeping check, which files are currently there, link to Data model
    :messages: same as files but for chat messages
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
    
    files = models.JSONField()
    messages = models.JSONField()

    dependenciesIn = models.ManyToManyField("self", symmetrical=False, related_name="processesIn")
    dependenciesOut = models.ManyToManyField("self", symmetrical=False, related_name="processesOut")
    
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

    ###################################################
    class Meta:
        indexes = [
            models.Index(fields=["processID"], name="processIDs_idx"),
        ]

    ###################################################
    def __str__(self):
        return ""
    
    def toDict(self):
        return {ProcessDescription.processID: self.processID, 
                ProcessDescription.project: self.project.toDict(), 
                ProcessDescription.serviceDetails: self.serviceDetails, 
                ProcessDescription.processStatus: self.processStatus,
                ProcessDescription.serviceType: self.serviceType,
                ProcessDescription.serviceStatus: self.serviceStatus,
                ProcessDescription.processDetails: self.processDetails,
                ProcessDescription.dependenciesIn: [ process.processID for process in self.dependenciesIn.all()],
                ProcessDescription.dependenciesOut: [ process.processID for process in self.dependenciesOut.all()],
                ProcessDescription.client: self.client,
                ProcessDescription.contractor: self.contractor.name if self.contractor is not None else "",
                ProcessDescription.files: self.files,
                ProcessDescription.messages: self.messages,
                ProcessDescription.createdWhen: str(self.createdWhen), ProcessDescription.updatedWhen: str(self.updatedWhen), ProcessDescription.accessedWhen: str(self.accessedWhen)}
    
###################################################
class ManyToManySimulation():
    """
    Simulate a many to many field for session

    """
    ###################################################
    def __init__(self) -> None:
        self._arrayOfProcesses = []
    
    ###################################################
    def initialize(self, dependencies:list[str]) -> None:
        self._arrayOfProcesses = copy.deepcopy(dependencies)

    ###################################################
    def add(self, pi:ProcessInterface):
        """
        Add a process interface to the array
        """
        self._arrayOfProcesses.append(pi.processID)
    
    ###################################################
    def all(self) -> list[str]:
        """
        Get array for iteration
        """
        return self._arrayOfProcesses



###################################################
class ProcessInterface():
    """
    Process management class interface.
    
    :processID: Unique ID for that process, primary key
    :project: ProjectInterface of project that this process belongs to
    :processDetails: Name of the process and stuff
    :processStatus: How everything is going in general
    :serviceDetails: Details for that service
    :serviceStatus: How everything is going for the service
    :serviceType: Which service it is
    :client: Who started the process
    :files: Registrar keeping check, which files are currently there, link to Data model
    :messages: same as files but for chat messages
    :createdWhen: Automatically assigned date and time(UTC+0) when the entry is created
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the entry was fetched from the database, automatically set
    """
    ###################################################
    processID = ""
    
    project = ProjectInterface("","","")

    processDetails = {}
    processStatus = 0

    serviceDetails = {}
    serviceStatus = 0
    serviceType = 0

    dependenciesIn = ManyToManySimulation()
    dependenciesOut = ManyToManySimulation()

    client = ""
    
    files = {}
    messages = {"messages": []}

    createdWhen = ""
    updatedWhen = ""
    accessedWhen = ""

    ###################################################
    def __init__(self, project:ProjectInterface, processID:str, currentTime:str, client:str) -> None:
        self.processID = processID
        self.project = project
        self.processDetails = {"amount": 1}
        self.processStatus = 0
        self.serviceDetails = {}
        self.serviceStatus = 0
        self.serviceType = serviceManager.getNone()
        self.dependenciesIn = ManyToManySimulation()
        self.dependenciesOut = ManyToManySimulation()
        self.client = client
        self.files = {}
        self.messages = {"messages": []}
        self.createdWhen = currentTime
        self.updatedWhen = currentTime
        self.accessedWhen = currentTime

    ###################################################
    def setValues(self, processDetails, processStatus, serviceDetails, serviceStatus, serviceType, client, files, messages, dependenciedIn, dependenciesOut, updatedWhen, accessedWhen) -> None:
        """
        Setter

        """
        self.processDetails = processDetails
        self.processStatus = processStatus
        self.serviceDetails = serviceDetails
        self.serviceStatus = serviceStatus
        self.serviceType = serviceType
        self.client = client
        self.files = files
        self.messages = messages
        self.dependenciesIn.initialize(dependenciedIn)
        self.dependenciesOut.initialize(dependenciesOut)
        self.updatedWhen = updatedWhen
        self.accessedWhen = accessedWhen

    ###################################################
    def toDict(self):
        return {ProcessDescription.processID: self.processID, 
                ProcessDescription.serviceDetails: self.serviceDetails, 
                ProcessDescription.processStatus: self.processStatus,
                ProcessDescription.serviceType: self.serviceType,
                ProcessDescription.serviceStatus: self.serviceStatus,
                ProcessDescription.processDetails: self.processDetails,
                ProcessDescription.dependenciesIn: self.dependenciesIn.all(),
                ProcessDescription.dependenciesOut: self.dependenciesOut.all(),
                ProcessDescription.client: self.client,
                ProcessDescription.files: self.files,
                ProcessDescription.messages: self.messages,
                ProcessDescription.createdWhen: str(self.createdWhen), ProcessDescription.updatedWhen: str(self.updatedWhen), ProcessDescription.accessedWhen: str(self.accessedWhen)}
    
