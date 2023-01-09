from django.db import models

from .base import BaseModel

class Profile(BaseModel):
    name = models.CharField(max_length=30,primary_key=True)
    email = models.CharField(max_length=30)
    role = models.CharField(max_length=30)

    ###################################################
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = args[0]
        self.email = args[1]
        self.role = args[2]

    ###################################################
    def __init__(self) -> None:
        super().__init__()

    ###################################################
    def __str__(self):
        return self.name + " " + self.email + " " + self.role