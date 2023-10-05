"""
Part of Semper-KI software

Silvio Weging 2023

Contains: link to model files for django to handle
"""



#from django.db import models

from .modelFiles.profileModel import *
from .modelFiles.projectModels import *

#class BaseModel(models.Model):

#    class Meta:
#        abstract = True  # specify this model as an Abstract Model
#        app_label = 'backend_django'

# class Profile(models.Model):
#     name = models.CharField(max_length=30)
#     email = models.CharField(max_length=30)
#     role = models.CharField(max_length=30)
    
#     def createUser(self, *args):
#         self.name = args[0]
#         self.email = args[1]
#         self.role = args[2]

#     ###################################################
#     def __str__(self):
#         return self.name + " " + self.email + " " + self.role