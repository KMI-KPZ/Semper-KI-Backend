"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Model for orders of a user
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField

# class userOrdersType:
#     """
#     userOrders class

#     :arrayWithDicts: Contains the cart
#     """
#     arrayWithDicts = []

###################################################

class Orders(models.Model):
    """
    Order management class.
    
    :uID: Unique ID for that person returned by Auth0, primary key
    :orderIDs: IDs for every order of that user
    :userOrders: Orders from the cart including prices and everything
    :orderStatus: How everything is going
    :userCommunication: What was said by whom to whom and when
    :files: All URL Paths of files uploaded for an order
    :dates: Date created and updated for every order
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    """
    ###################################################
    uID = models.CharField(primary_key=True,max_length=256)
    orderIDs = ArrayField(models.CharField(max_length=256))
    userOrders = models.JSONField()
    orderStatus = models.JSONField()
    userCommunication = models.JSONField()
    files = models.JSONField()
    dates = models.JSONField()
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)
    ###################################################
    def __str__(self):
        return ""