"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Model for orders of a user
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField

###################################################
class OrderCollection(models.Model):
    """
    Order Collection class.
    
    :orderCollectionID: Unique ID for that order collection, primary key
    :status: Current state of the order collection
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    """
    orderCollectionID = models.CharField(primary_key=True,max_length=513)
    status = models.IntegerField()
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

###################################################
class Orders(models.Model):
    """
    Order management class.
    
    :orderID: Unique ID for that order, primary key
    :orderCollectionKey: Signals django to link that order to an order collection
    :userOrders: Orders from the cart including prices and everything
    :status: How everything is going
    :userCommunication: What was said by whom to whom and when
    :files: All URL Paths of files uploaded for an order
    :dates: Date created and updated for every order
    :createdWhen: Automatically assigned date and time(UTC+0) when the user first registered
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the user was fetched from the database, automatically set
    """
    ###################################################
    orderID = models.CharField(primary_key=True,max_length=513)
    orderCollectionKey = models.ForeignKey(OrderCollection, on_delete=models.CASCADE, related_name="orders")
    userOrders = models.JSONField()
    status = models.IntegerField()
    userCommunication = models.JSONField()
    files = models.JSONField()
    dates = models.JSONField()
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)
    ###################################################
    def __str__(self):
        return ""
    
