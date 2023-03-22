import json, random, base64, hashlib
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from .files import getUploadedFiles
from ..services import cmem, stl

#######################################################
class mockPicture():
    picturePath = "/public/static/media/testpicture.jpg"

    def __init__(self):
        if settings.PRODUCTION:
            self.backend_url = 'https://backend.semper-ki.org'
        else:
            self.backend_url = 'http://127.0.0.1:8000'
        self.mockPicturePath = self.backend_url+self.picturePath

testpicture = mockPicture()
#######################################################
def mockModels():

    tags = ["Tag1", "Tag2", "Tag3", "Tag4"]
    licenses = ["MIT", "GNU GPLv3", "Apache 2.0", "Corporate"]
    certificates = ["ISO1", "ISO2", "ISO3"]
    models = {"models": []}
    for i in range(20):
        title = "testmodel " + str(i)
        models["models"].append(
            {"id": hashlib.md5(title.encode()).hexdigest() ,"title": title, "tags": [random.choice(tags) for j in range(random.randint(1,4))], "date": "2023-02-01", "license": random.choice(licenses), "certificate": [random.choice(certificates) for j in range(random.randint(1,3))], "URI": testpicture.mockPicturePath}
        )
    return models
modelMock = mockModels()

#######################################################
def mockMaterials():
    materials = {"materials": []}

    materials["materials"].append({"id": hashlib.md5(b"ABS").hexdigest(), "title": "ABS", "propList": ["Tough", "Heat resistant", "Impact resistant"], "URI": testpicture.mockPicturePath})
    materials["materials"].append({"id": hashlib.md5(b"PLA").hexdigest(),"title": "PLA", "propList": ["Rigid", "Brittle", "Biodegradable"], "URI": testpicture.mockPicturePath})
    materials["materials"].append({"id": hashlib.md5(b"Standard resin").hexdigest(),"title": "Standard resin", "propList": ["High resolution", "Smooth"], "URI": testpicture.mockPicturePath})
    materials["materials"].append({"id": hashlib.md5(b"Polyurethane resin").hexdigest(),"title": "Polyurethane resin", "propList": ["Long-term durability", "UV stable", "Sterilizability"], "URI": testpicture.mockPicturePath})
    materials["materials"].append({"id": hashlib.md5(b"Titanium").hexdigest(),"title": "Titanium", "propList": ["Lightweight", "Strong", "Heat resistant"], "URI": testpicture.mockPicturePath})
    materials["materials"].append({"id": hashlib.md5(b"Stainless steel").hexdigest(),"title": "Stainless steel", "propList": ["Strong", "Resistant to corrosion", "High ductility"], "URI": testpicture.mockPicturePath})
    
    return materials
materialMock = mockMaterials()

#######################################################
def mockPostProcessing():
    postProcessing = {"postProcessing": []}

    possibleValues = ["selection1", "selection2", "selection3"]
    processingOptions = ["selection", "number", "text"]

    for i in range(3):
        title = "postProcessing " + str(i)
        postProcessing["postProcessing"].append({"id": hashlib.md5(title.encode()).hexdigest(), "title": title, "checked": False, "selectedValue": "", "valueList": [random.choice(possibleValues) for j in range(random.randint(1,3))], "type": processingOptions[0], "URI": testpicture.mockPicturePath})
    for i in range(3):
        title = "postProcessing " + str(i+3)
        postProcessing["postProcessing"].append({"id": hashlib.md5(title.encode()).hexdigest(), "title": title, "checked": False, "selectedValue": "", "valueList": [], "type": processingOptions[1], "URI": testpicture.mockPicturePath})
    for i in range(3):
        title = "postProcessing " + str(i+6)
        postProcessing["postProcessing"].append({"id": hashlib.md5(title.encode()).hexdigest(), "title": title, "checked": False, "selectedValue": "", "valueList": [], "type": processingOptions[2], "URI": testpicture.mockPicturePath})

    return postProcessing
postProcessingMock = mockPostProcessing()

#######################################################
def getProcessData(request):
    """
    Try to filter all according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Models accoding to filters via JSON
    :rtype: JSON

    """
    # get filters set by user
    filters = json.loads(request.body.decode("utf-8"))
    # Filter name is in question -> title, selected stuff is in "answer"
    filtersForSparql = []
    for entry in filters["filters"]:
        filtersForSparql.append([entry["question"]["title"], entry["answer"]])
    #TODO ask via sparql with most general filter and then iteratively filter response
    
    # mockup here:
    filters.update(modelMock)
    filters.update(materialMock)
    filters.update(postProcessingMock)

    # TODO: gzip this 
    return JsonResponse(filters)

#######################################################
def getUploadedModel(file):
    """
    Get uploaded model

    :return: uploaded model
    :rtype: Dictionary

    """

    models = {"models": []}
    model = {"title": "", "tags": [], "date": "1800-01-01", "license": "", "certificate": [], "URI": ""}
    
    now = timezone.now()
    binaryJpg = stl.stlToJpg(file[1])
    b64Jpg = base64.b64encode(binaryJpg)
    model = {"title": file[0], "tags": [], "date": str(now.year)+"-"+str(now.month)+"-"+str(now.day), "license": "", "certificate": [], "URI": str(b64Jpg)}

    # stl.binToJpg(b64Jpg) # sanity check

    models["models"].append(model)
    return model

#######################################################
def getModels(request):
    """
    Try to filter 3d-models according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Models accoding to filters via JSON
    :rtype: JSON

    """
    # get filters set by user
    filters = json.loads(request.body.decode("utf-8"))

    # if user uploaded a file, show that instead
    response = getUploadedFiles(request.session.session_key)
    if response is not None:
        filters.update(getUploadedModel(response))
    else:
        # Filter name is in question -> title, selected stuff is in "answer"
        filtersForSparql = []
        for entry in filters["filters"]:
            filtersForSparql.append([entry["question"]["title"], entry["answer"]])
        #TODO ask via sparql with most general filter and then iteratively filter response
        
        # mockup here:
        filters.update(modelMock)
    
    # TODO: gzip this 
    return JsonResponse(filters)

#######################################################
def getMaterials(request):
    """
    Try to filter materials according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Materials accoding to filters via JSON
    :rtype: JSON

    """
    # get filters set by user
    filters = json.loads(request.body.decode("utf-8"))
    # Filter name is in question -> title, selected stuff is in "answer"
    filtersForSparql = []
    for entry in filters["filters"]:
        filtersForSparql.append([entry["question"]["title"], entry["answer"]])
    #TODO ask via sparql with most general filter and then iteratively filter response


    # mockup here:
    filters.update(materialMock)
    
    # TODO: gzip this 
    return JsonResponse(filters)

#######################################################
def getPostProcessing(request):
    """
    Try to filter post processing according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Materials accoding to filters via JSON
    :rtype: JSON

    """
    # get filters set by user
    filters = json.loads(request.body.decode("utf-8"))
    # Filter name is in question -> title, selected stuff is in "answer"
    filtersForSparql = []
    for entry in filters["filters"]:
        filtersForSparql.append([entry["question"]["title"], entry["answer"]])
    #TODO ask via sparql with most general filter and then iteratively filter response

    # mockup here:
    filters.update(postProcessingMock)
    
    # TODO: gzip this 
    return JsonResponse(filters)

#######################################################
def getFilters(request):
    """
    Try to filter 3d-models according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Models accoding to filters via JSON
    :rtype: JSON

    """
    # get filters set by user
    filters = json.loads(request.body.decode("utf-8"))
    # Filter name is in question -> title, selected stuff is in "answer"
    filtersForSparql = []
    for entry in filters["filters"]:
        filtersForSparql.append([entry["question"]["title"], entry["answer"]])
    #TODO ask via sparql with most general filter and then iteratively filter response
    
    # TODO: gzip this 
    return JsonResponse(filters)