"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Mockups for various stuff
"""

from django.conf import settings
from django.utils import timezone
import random

from Generic_Backend.code_General.utilities import crypto
from code_SemperKI.utilities.basics import testPicture

#######################################################
def mockModels():

    tags = ["Tag1", "Tag2", "Tag3", "Tag4"]
    licenses = ["MIT", "GNU GPLv3", "Apache 2.0", "Corporate"]
    certificates = ["ISO1", "ISO2", "ISO3"]
    models = {"models": []}
    for i in range(20):
        title = "testmodel " + str(i)
        models["models"].append(
            {"id": crypto.generateMD5(title) ,"title": title, "tags": [random.choice(tags) for j in range(random.randint(1,4))], "date": "2023-02-01", "licenses": [random.choice(licenses) for j in range(random.randint(1,3))], "certificates": [random.choice(certificates) for j in range(random.randint(1,3))], "URI": testPicture, "createdBy": "kiss"}
        )
    return models
modelMock = mockModels()

#######################################################
def getEmptyMockModel():
    now = timezone.now()
    return {"id": "","title": "", "tags": [], "date": str(now.year)+"-"+str(now.month)+"-"+str(now.day), "licenses": [], "certificates": [], "URI": "", "createdBy": "kiss"}


