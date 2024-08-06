"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Model for database version of the Knowledge Graph
"""

import json, enum
from django.db import models
from django.contrib.postgres.fields import ArrayField

from Generic_Backend.code_General.utilities.customStrEnum import StrEnumExactlyAsDefined

##################################################
class NodeDescription(StrEnumExactlyAsDefined):
    """
    What does a node consists of?

    """
    nodeID = enum.auto()
    nodeName = enum.auto()
    nodeType = enum.auto()
    context = enum.auto()
    properties = enum.auto()
    edges = enum.auto()
    createdWhen = enum.auto()
    updatedWhen = enum.auto()
    accessedWhen = enum.auto()

##################################################
class NodeType(StrEnumExactlyAsDefined):
    """
    What are the possible types of a node?
    
    """
    organization = enum.auto()
    printer = enum.auto()
    material = enum.auto()
    additionalRequirement = enum.auto()
    color = enum.auto()

##################################################
class NodeProperties(StrEnumExactlyAsDefined):
    """
    What are the properties, a node can have?

    """
    foodSafe = enum.auto() #"FDA;10/2011"
    heatResistant = enum.auto() #250
    flexible = enum.auto() # 0.5Z50;0.7Z100;4.8XY50;3.7XY100
    smooth = enum.auto() # 20Ra
    eModul = enum.auto() # 1358Z;2030XY
    poissonRatio = enum.auto() #0.35
    color = enum.auto() # 9005RAL;Black

    buildVolume = enum.auto() # 100x100x100
    technology = enum.auto() # FDM

##################################################
class Node(models.Model):
    """
    The class of a node containing different information, depending on it's type.
    
    :nodeID: The ID for that node
    :nodeName: The name of that node
    :nodeType: The type of the node as described in the respective Enum
    :context: Some information about the node, can be anything
    :properties: The properties that this node has, depends on the type
    :edges: The nodes connected to this one, symmetrical (so it's an undirected graph)
    :createdWhen: Automatically assigned date and time(UTC+0) when the entry is created
    :updatedWhen: Date and time at which the entry was updated
    :accessedWhen: Last date and time the entry was fetched from the database, automatically set
    """
    nodeID = models.CharField(primary_key=True,max_length=513)
    nodeName = models.CharField(max_length=513)
    nodeType = models.CharField(max_length=513)
    context = models.CharField(max_length=10000)
    properties = models.JSONField()
    edges = models.ManyToManyField("self", symmetrical=True)
    createdWhen = models.DateTimeField(auto_now_add=True)
    updatedWhen = models.DateTimeField()
    accessedWhen = models.DateTimeField(auto_now=True)

    ###################################################
    class Meta:
        indexes = [
            models.Index(fields=["nodeID"], name="nodeID_idx"),
            models.Index(fields=["nodeType"], name="node_type_idx"),
            models.Index(fields=["properties"], name="node_properties_idx")
        ]

    ###################################################
    def __str__(self):
        return ""
    
    ###################################################
    def toDict(self):
        """
        Return only the node information, not the whole graph

        """
        return {
            NodeDescription.nodeID: self.nodeID,
            NodeDescription.nodeName: self.nodeName,
            NodeDescription.nodeType: self.nodeType,
            NodeDescription.context: self.context,
            NodeDescription.properties: self.properties,
            NodeDescription.createdWhen: str(self.createdWhen), 
            NodeDescription.updatedWhen: str(self.updatedWhen), 
            NodeDescription.accessedWhen: str(self.accessedWhen)
        }