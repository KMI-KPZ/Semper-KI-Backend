from django.db import models

class Profile(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    role = models.CharField(max_length=30)
    
    def createUser(self, *args):
        self.name = args[0]
        self.email = args[1]
        self.role = args[2]

    ###################################################
    def __str__(self):
        return self.name + " " + self.email + " " + self.role

    ###################################################
    def toDict(self):
        return {"name": self.name, "email" : self.email,  "type": self.role}