"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Model for user and manufacturer profiles, as well as their meta classes
"""
import json
from django.db import models

from backend_django.modelFiles.orders import OrderCollection

# Table for regular Users
###################################################
class User(models.Model):
    """
    Profile management class for regular users.
    
    :subID: Unique ID for that person returned by Auth0, primary key
    :hashedID: SHA-512 hashed value of the subID for anonymous identification
    :name: Nickname returned by Auth0, used for filter searches in DB
    :email: E-Mail with which the user registered themselves
    :organization: The Stakeholder that user belongs to
    :role: Role assigned to the user
    :rights: The rights that user has
    :address: Where to find the user
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    """
    subID = models.CharField(primary_key=True,max_length=100)
    hashedID = models.CharField(max_length=513)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    rights = models.JSONField()
    address = models.JSONField()
    orders = models.ManyToManyField(OrderCollection)
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

    ###################################################
    def __str__(self):
        return self.hashedID + " " + self.name + " " + self.email + " " + self.organization + " " + self.role + " " + json.dumps(self.rights) + " " + json.dumps(self.address) + " " + str(self.createdWhen) + " " + str(self.updatedWhen) + " " + str(self.accessedWhen)

    ###################################################
    def toDict(self):
        return {"hashedID": self.hashedID, "name": self.name, "email" : self.email, "organization": self.organization,  "type": self.role, "rights": json.dumps(self.rights), "address": json.dumps(self.address), "created": self.createdWhen, "updated": self.updatedWhen, "accessed": self.accessedWhen}

#TODO solve this more elegantly!

# Table for stakeholders which can contain Users
###################################################
class Stakeholder(models.Model):
    """
    Profile management class for stakeholder.
    
    :subID: Unique ID for that stakeholder returned by Auth0, primary key
    :hashedID: SHA-512 hashed value of the subID for anonymous identification
    :name: Nickname returned by Auth0, used for filter searches in DB
    :email: E-Mail with which the user registered themselves
    :address: Where to find the user
    :users: Link to users belonging to that stakeholder
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    """
    subID = models.CharField(primary_key=True,max_length=100)
    hashedID = models.CharField(max_length=513)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.JSONField()
    users = models.ManyToManyField(User)
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

#Table for Manufacturers
###################################################
class Manufacturer(models.Model):
    """
    Profile management class for manufacturers.
    
    :subID: Unique ID for that person returned by Auth0, primary key
    :hashedID: SHA-512 hashed value of the subID for anonymous identification
    :name: Nickname returned by Auth0, used for filter searches in DB
    :email: E-Mail with which the user registered themselves
    :address: Where to find the manufacturer
    :users: Link to users belonging to that manufacturer
    :uri: Representation link inside the knowledge graph
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    """
    subID = models.CharField(primary_key=True,max_length=100)
    hashedID = models.CharField(max_length=513)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.JSONField()
    users = models.ManyToManyField(User)
    uri = models.CharField(max_length=200)
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)