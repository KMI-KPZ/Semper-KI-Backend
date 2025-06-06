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

#######################################################
def mockMaterials():
    materials = {"materials": []}

    materials["materials"].append({"id": crypto.generateMD5("PLA - black"), "title": "PLA - black", "propList": [], "imgPath": settings.S3_STATIC_URL+"media/PLA_black.jpg"})
    materials["materials"].append({"id": crypto.generateMD5("PLA - white"), "title": "PLA - white", "propList": [], "imgPath": settings.S3_STATIC_URL+"media/PLA_white.jpg"})
    materials["materials"].append({"id": crypto.generateMD5("PLA - gray"), "title": "PLA - gray", "propList": [], "imgPath": settings.S3_STATIC_URL+"media/PLA_grey.jpg"})
    materials["materials"].append({"id": crypto.generateMD5("PLA - red"), "title": "PLA - red", "propList": [], "imgPath": settings.S3_STATIC_URL+"media/PLA_red.jpg"})
    materials["materials"].append({"id": crypto.generateMD5("PLA - blue"), "title": "PLA - blue", "propList": [], "imgPath": settings.S3_STATIC_URL+"media/PLA_blue.jpg"})
    materials["materials"].append({"id": crypto.generateMD5("PLA - yellow"), "title": "PLA - yellow", "propList": [], "imgPath": settings.S3_STATIC_URL+"media/PLA_yellow.jpg"})
    materials["materials"].append({"id": crypto.generateMD5("PLA - green"), "title": "PLA - green", "propList": [], "imgPath": settings.S3_STATIC_URL+"media/PLA_green.jpg"})

    """
    materials["materials"].append({"id": crypto.generateMD5("ABS"), "title": "ABS", "propList": ["Tough", "Heat resistant", "Impact resistant"], "URI": testpicture})
    materials["materials"].append({"id": crypto.generateMD5("PLA"),"title": "PLA", "propList": ["Rigid", "Brittle", "Biodegradable"], "URI": testpicture})
    materials["materials"].append({"id": crypto.generateMD5("Standard resin"),"title": "Standard resin", "propList": ["High resolution", "Smooth"], "URI": testpicture})
    materials["materials"].append({"id": crypto.generateMD5("Polyurethane resin"),"title": "Polyurethane resin", "propList": ["Long-term durability", "UV stable", "Sterilizability"], "URI": testpicture})
    materials["materials"].append({"id": crypto.generateMD5("Titanium"),"title": "Titanium", "propList": ["Lightweight", "Strong", "Heat resistant"], "URI": testpicture})
    materials["materials"].append({"id": crypto.generateMD5("Stainless steel"),"title": "Stainless steel", "propList": ["Strong", "Resistant to corrosion", "High ductility"], "URI": testpicture})
    """

    return materials
materialMock = mockMaterials()

#######################################################
def mockPostProcessing():
    postProcessing = {"postProcessings": []}

    possibleValues = ["selection1", "selection2", "selection3"]
    processingOptions = ["selection", "number", "text"]

    postProcessing["postProcessings"].append({"id": crypto.generateMD5("None"), "title": "None", "checked": False, "selectedValue": "", "valueList": [], "type": "text", "imgPath": testPicture})
    postProcessing["postProcessings"].append({"id": crypto.generateMD5("Remove Support"), "title": "Remove Support", "checked": False, "selectedValue": "", "valueList": [], "type": "text", "imgPath": testPicture})

    """ for i in range(3):
        title = "postProcessing " + str(i)
        postProcessing["postProcessing"].append({"id": crypto.generateMD5(title), "title": title, "checked": False, "selectedValue": "", "valueList": [random.choice(possibleValues) for j in range(random.randint(1,3))], "type": processingOptions[0], "URI": testpicture})
    for i in range(3):
        title = "postProcessing " + str(i+3)
        postProcessing["postProcessing"].append({"id": crypto.generateMD5(title), "title": title, "checked": False, "selectedValue": "", "valueList": [], "type": processingOptions[1], "URI": testpicture})
    for i in range(3):
        title = "postProcessing " + str(i+6)
        postProcessing["postProcessing"].append({"id": crypto.generateMD5(title), "title": title, "checked": False, "selectedValue": "", "valueList": [], "type": processingOptions[2], "URI": testpicture})
 """
    return postProcessing
postProcessingMock = mockPostProcessing()

#######################################################
def mockPrices(selection):
    mockFactors = {"materials": {
                "ABS": 1,
                "PLA": 2,
                "Standard resin": 3,
                "Polyurethane resin": 4,
                "Titanium": 5,
                "Stainless steel": 6
            },
            "postProcessing": {
                "None" : 0,
                "postProcessing 0": 1,
                "postProcessing 1": 2,
                "postProcessing 2": 3,
                "postProcessing 3": 4,
                "postProcessing 4": 3,
                "postProcessing 5": 3,
                "postProcessing 6": 3,
                "postProcessing 7": 3,
                "postProcessing 8": 3
            }
    }

    mockPrices = {
        "material": mockFactors["materials"][selection["material"]["title"]] * 10,
        "postProcessing": mockFactors["postProcessing"][selection["postProcessings"][0]["title"]] * 5,
        "logistics": random.randint(1,100)
    }

    mockPrices["totalPrice"] = mockPrices["material"] + mockPrices["postProcessing"]

    return mockPrices["totalPrice"]
    #return mockPrices

#######################################################
def mockLogistics(selection):
    mockFactors = {"materials": {
                "ABS": 1,
                "PLA": 2,
                "Standard resin": 3,
                "Polyurethane resin": 4,
                "Titanium": 5,
                "Stainless steel": 6
            },
            "postProcessing": {
                "None" : 0,
                "postProcessing 0": 1,
                "postProcessing 1": 2,
                "postProcessing 2": 3,
                "postProcessing 3": 4,
                "postProcessing 4": 3,
                "postProcessing 5": 3,
                "postProcessing 6": 3,
                "postProcessing 7": 3,
                "postProcessing 8": 3
            }
    }

    mockTimes = {
        "material": mockFactors["materials"][selection["material"]["title"]] * 5,
        "postProcessing": mockFactors["postProcessing"][selection["postProcessings"][0]["title"]] * 1,
        "delivery": random.randint(1,10)
    }

    mockTimes["production"] = mockTimes["material"] + mockTimes["postProcessing"]
    return mockTimes["production"] + mockTimes["delivery"]
    #return mockTimes

#######################################################
def mockPrinter():
    outList = [{"Property 1": 5}, "Property 2", {"Property 3": "Test", "Property 4": [1,10]}, {"Property 5": [{"Property 6": "Test2"},{"Property 7": 2}]}]

    return outList

#######################################################
def mockMaterial():
    return mockPrinter()

