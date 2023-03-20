import json, random, base64
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from .files import getUploadedFiles
from ..services import cmem, stl


#######################################################
def mockModels():
    tags = ["tag1", "tag2", "tag3", "tag4"]
    licenses = ["MIT", "GNU GPLv3", "Apache 2.0", "Corporate"]
    certificates = ["ISO1", "ISO2", "ISO3"]
    URIs = ["https://i0.wp.com/letsprint3d.net/wp-content/uploads/2017/04/benchy.jpg?resize=663%2C373&ssl=1","https://cdn.thingiverse.com/assets/66/33/72/e5/71/featured_preview_pika2.jpg", "https://cdn.thingiverse.com/assets/53/4d/bc/af/d8/featured_preview_IMG_20200405_112754.jpg"]

    models = {"models": []}
    for i in range(20):
        models["models"].append(
            {"title": "testmodel " + str(i), "tags": [random.choice(tags) for j in range(random.randint(1,4))], "date": "2023-02-01", "license": random.choice(licenses), "certificate": [random.choice(certificates) for j in range(random.randint(1,3))], "URI": random.choice(URIs)}
        )
    return models

#######################################################
def mockMaterials():
    materials = {"materials": []}

    materials["materials"].append({"title": "ABS", "propList": ["Tough", "Heat resistant", "Impact resistant"], "URI": "https://res.cloudinary.com/all3dp/image/upload/w_550,q_90,f_auto/v1662649964/gallery/New%20images/Revised/ABS.jpg"})
    materials["materials"].append({"title": "PLA", "propList": ["Rigid", "Brittle", "Biodegradable"], "URI": "https://res.cloudinary.com/all3dp/image/upload/w_550,q_90,f_auto/v1663921490/gallery/New%20images/Revised/PLA.jpg"})
    materials["materials"].append({"title": "Nylon", "propList": ["Strong", "Lightweight", "Partially flexible", "Heat resistant", "Impact resistant"], "URI": "https://res.cloudinary.com/all3dp/image/upload/w_550,q_90,f_auto/v1662650032/gallery/New%20images/Revised/SLS_PA12.jpg"})
    materials["materials"].append({"title": "Standard resin", "propList": ["High resolution", "Smooth"], "URI": "https://res.cloudinary.com/all3dp/image/upload/w_550,q_90,f_auto/v1662649994/gallery/New%20images/Revised/Highb_detail_resin.jpg"})
    materials["materials"].append({"title": "Polyurethane resin", "propList": ["Long-term durability", "UV stable", "Sterilizability"], "URI": "https://i0.wp.com/i.all3dp.com/wp-content/uploads/2016/08/27050929/Formlabs-Form-2-Build.jpg?ssl=1"})
    materials["materials"].append({"title": "Titanium", "propList": ["Lightweight", "Strong", "Heat resistant"], "URI": "https://res.cloudinary.com/all3dp/image/upload/w_550,q_90,f_auto/v1662650037/gallery/New%20images/Revised/Titanium_raw.jpg"})
    materials["materials"].append({"title": "Stainless steel", "propList": ["Strong", "Resistant to corrosion", "High ductility"], "URI": "https://res.cloudinary.com/all3dp/image/upload/w_550,q_90,f_auto/v1662649951/gallery/New%20images/Revised/17-4_PH_SS.jpg"})
    
    return materials

#######################################################
def mockPostProcessing():
    postProcessing = {"postProcessing": []}

    possibleValues = ["selection1", "selection2", "selection3"]
    processingOptions = ["selection", "number", "text"]

    for i in range(3):
        postProcessing["postProcessing"].append({"title": "postProcessing " + str(i), "checked": False, "selectedValue": "", "valueList": [random.choice(possibleValues) for j in range(random.randint(1,3))], "type": processingOptions[0], "URI": "https://res.cloudinary.com/all3dp/image/upload/w_550,q_90,f_auto/gallery/pla.jpg"})
    for i in range(3):
        postProcessing["postProcessing"].append({"title": "postProcessing " + str(i+3), "checked": False, "selectedValue": "", "valueList": [], "type": processingOptions[1], "URI": "https://res.cloudinary.com/all3dp/image/upload/w_550,q_90,f_auto/gallery/sanded_pla.jpg"})
    for i in range(3):
        postProcessing["postProcessing"].append({"title": "postProcessing " + str(i+6), "checked": False, "selectedValue": "", "valueList": [], "type": processingOptions[2], "URI": "https://res.cloudinary.com/all3dp/image/upload/w_550,q_90,f_auto/v1661938321/gallery/New%20images/SLS_polished.jpg"})


    return postProcessing

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
    filters.update(mockModels())
    filters.update(mockMaterials())
    filters.update(mockPostProcessing())

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
        filters.update(mockModels())
    
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
    filters.update(mockMaterials())
    
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
    filters.update(mockPostProcessing())
    
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