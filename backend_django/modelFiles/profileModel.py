"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Model for user and manufacturer profiles, as well as their meta classes
"""
import json
from django.db import models
from django.contrib.postgres.fields import ArrayField

from ..modelFiles import ordersModel

# Table for regular Users
###################################################
class User(models.Model):
    """
    Profile management class for regular users.
    
    :subID: Unique ID for that person returned by Auth0, primary key
    :hashedID: SHA-512 hashed value of the subID for anonymous identification
    :name: Nickname returned by Auth0, used for filter searches in DB
    :email: E-Mail with which the user registered themselves
    :organizations: The organizations that the user belongs to
    :details: Adress, ...
    :orders: The OrderCollections that this user submitted, only added if the user is not in an organization
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    :lastSeen: When was the user last online, set manually
    """
    subID = models.CharField(primary_key=True,max_length=100)
    hashedID = models.CharField(max_length=513)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    organizations = ArrayField(models.CharField(max_length=513))
    details = models.JSONField()
    orders = models.ManyToManyField(ordersModel.OrderCollection)
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)
    lastSeen = models.DateTimeField()

    ###################################################
    def __str__(self):
        return self.hashedID + " " + self.name + " " + self.email + " " + str(self.organizations) + " " + json.dumps(self.details) + " " + str(self.createdWhen) + " " + str(self.updatedWhen) + " " + str(self.accessedWhen) + " " + str(self.lastSeen)

    ###################################################
    def toDict(self):
        return {"hashedID": self.hashedID, "name": self.name, "email" : self.email, "organizations": self.organizations, "details": json.dumps(self.details), "created": self.createdWhen, "updated": self.updatedWhen, "accessed": self.accessedWhen, "lastSeen": self.lastSeen}

#Table for Organizations
###################################################
class Organization(models.Model):
    """
    Profile management class for organizations.
    
    :subID: Unique ID for that person returned by Auth0, primary key
    :hashedID: SHA-512 hashed value of the subID for anonymous identification
    :name: Nickname returned by Auth0, used for filter searches in DB
    :email: E-Mail with which the user registered themselves
    :details: Adress, tax id and so on
    :users: Link to users belonging to that organization
    :canManufacture: True if this organization can manufacture something
    :ordersSubmitted: OrderCollections that this organization submitted
    :ordersReceived: Orders that this organization received
    :uri: Representation link inside the knowledge graph
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    """
    subID = models.CharField(primary_key=True,max_length=100)
    hashedID = models.CharField(max_length=513)
    name = models.CharField(max_length=100)
    details = models.JSONField()
    users = models.ManyToManyField(User)
    canManufacture = models.BooleanField(default=False)
    ordersSubmitted = models.ManyToManyField(ordersModel.OrderCollection)
    ordersReceived = models.ManyToManyField(ordersModel.Orders)
    uri = models.CharField(max_length=200)
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

    ###################################################
    def __str__(self):
        return self.hashedID + " " + self.name + " " + json.dumps(self.details) + " " + "canManufacturer: " + str(self.canManufacture) + " " + str(self.createdWhen) + " " + str(self.updatedWhen) + " " + str(self.accessedWhen)

    ###################################################
    def toDict(self):
        return {"hashedID": self.hashedID, "name": self.name, "details": json.dumps(self.details), "canManufacturer": self.canManufacture, "created": self.createdWhen, "updated": self.updatedWhen, "accessed": self.accessedWhen}
