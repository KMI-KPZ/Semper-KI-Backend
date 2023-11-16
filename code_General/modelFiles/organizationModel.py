"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Model for organizations
"""
import json
from django.db import models
from django.contrib.postgres.fields import ArrayField

from .userModel import User

#Table for Organizations
###################################################
class Organization(models.Model):
    """
    Profile management class for organizations.
    
    :subID: Unique ID for that person returned by Auth0, primary key
    :hashedID: SHA-512 hashed value of the subID for anonymous identification
    :name: Nickname returned by Auth0, used for filter searches in DB
    :details: Adress, tax id and so on
    :users: Link to users belonging to that organization
    :supportedServices: Array of service codes that this organization supports
    :uri: Representation link inside the knowledge graph
    :createdWhen: Automatically assigned date and time(UTC+0) when the entry is created
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the data was fetched from the database, automatically set
    """
    subID = models.CharField(primary_key=True,max_length=100)
    hashedID = models.CharField(max_length=513)
    name = models.CharField(max_length=100)
    details = models.JSONField()
    users = models.ManyToManyField(User)
    supportedServices = ArrayField(models.IntegerField())
    uri = models.CharField(max_length=200)
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

    ###################################################
    def __str__(self):
        return self.hashedID + " " + self.name + " " + json.dumps(self.details) + " " + "supportedServices: " + str(self.supportedServices) + " " + str(self.createdWhen) + " " + str(self.updatedWhen) + " " + str(self.accessedWhen)

    ###################################################
    def toDict(self):
        return {"hashedID": self.hashedID, "name": self.name, "details": json.dumps(self.details), "supportedServices": self.supportedServices, "created": self.createdWhen, "updated": self.updatedWhen, "accessed": self.accessedWhen}
