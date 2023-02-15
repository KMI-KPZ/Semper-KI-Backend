from django.db import models

# Table for regular Users
class Profile(models.Model):
    """
    Profile management class.
    
    :subID: Unique ID for that person returned by Auth0, primary key
    :name: Nickname returned by Auth0, used for filter searches in DB
    :email: E-Mail with which the user registered themselves
    :role: Role assigned to the user, can be regular, manufacturer, ...
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    """
    subID = models.CharField(primary_key=True,max_length=100)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

    ###################################################
    def __str__(self):
        return self.subID + " " + self.name + " " + self.email + " " + self.role + " " + str(self.createdWhen) + " " + str(self.updatedWhen) + " " + str(self.accessedWhen)

    ###################################################
    def toDict(self):
        return {"subID": self.subID, "name": self.name, "email" : self.email,  "type": self.role, "created": self.createdWhen, "updated": self.updatedWhen, "accessed": self.accessedWhen}

# TODO: Table for Manufacturers