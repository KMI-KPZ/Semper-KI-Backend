"""
Part of Semper-KI software

Silvio Weging 2023

Contains: URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from .handlers.public.resources import orga, onto, kgDBAM
from .handlers.public import materials, checkService, filter, model, postProcessings

from code_SemperKI.urls import paths, urlpatterns


newPaths = {
    #"getProcessData": ('public/getProcessData/',filter.getProcessData),
    #"getModels": ('public/getModels/',filter.getModels),
    #"getFilters": ('public/getFilters/',filter.getFilters),
    "getMaterials": ('public/service/additive-manufacturing/material/get/',materials.retrieveMaterialsWithFilter),
    "setMaterial": ('public/service/additive-manufacturing/material/set/',materials.setMaterialSelection),
    "deleteMaterial": ('public/service/additive-manufacturing/material/delete/<str:projectID>/<str:processID>/<str:materialID>/',materials.deleteMaterialFromSelection),

    "getPostProcessings": ('public/service/additive-manufacturing/post-processing/get/',postProcessings.retrievePostProcessingsWithFilter),
    "setPostProcessing": ('public/service/additive-manufacturing/post-processing/set/',postProcessings.setPostProcessingSelection),
    "deletePostProcessing": ('public/service/additive-manufacturing/post-processing/delete/<str:projectID>/<str:processID>/<str:postProcessingID>/',postProcessings.deletePostProcessingFromSelection),

    "uploadModel": ("public/service/additive-manufacturing/model/upload/",model.uploadModels),
    "deleteModel": ("public/service/additive-manufacturing/model/delete/<str:projectID>/<str:processID>/<str:fileID>/",model.deleteModel),
    "remeshSTLToTetraheadras": ("public/service/additive-manufacturing/model/remeshSTLToTetraheadras/<str:projectID>/<str:processID>/<str:fileID>/", model.remeshSTLToTetraheadras),
    "getModelRepository": ("public/service/additive-manufacturing/model/repository/get/", model.getModelRepository),

    #"checkPrintability": ("public/checkPrintability/",checkService.),
    #"checkPrices": ("public/checkPrices/",checkService.checkPrice),
    #"checkLogistics": ("public/checkLogistics/",checkService.checkLogistics),
    "checkModel": ("public/service/additive-manufacturing/model/check/<str:projectID>/<str:processID>/<str:fileID>/", checkService.checkModel),
    #"checkModelTest": ("public/checkModelTest/", checkService.getChemnitzData),

    "getPropertyDefinitionFrontend": ("public/service/additive-manufacturing/resources/onto/nodes/properties/get/by-type/<str:nodeType>/", kgDBAM.getPropertyDefinitionFrontend),
    
    "onto_getResources": ("public/service/additive-manufacturing/resources/onto/admin/nodes/get/by-type/<str:resourceType>/",onto.onto_getResources),
    "onto_getNodeViaID": ("public/service/additive-manufacturing/resources/onto/admin/nodes/get/by-id/<str:nodeID>/", onto.onto_getNodeViaID),
    "onto_getAssociatedResources": ("public/service/additive-manufacturing/resources/onto/admin/nodes/neighbors/get/<str:nodeID>/<str:resourceType>/", onto.onto_getAssociatedResources),
    "onto_addEdge": ("public/service/additive-manufacturing/resources/onto/admin/edge/create/",onto.onto_addEdge),
    "onto_removeEdge": ("public/service/additive-manufacturing/resources/onto/admin/edge/delete/<str:entity1ID>/<str:entity2ID>/",onto.onto_removeEdge),
    "onto_addNode": ("public/service/additive-manufacturing/resources/onto/admin/nodes/create/",onto.onto_addNode),
    "onto_updateNode": ("public/service/additive-manufacturing/resources/onto/admin/nodes/update/",onto.onto_updateNode),
    "onto_deleteNode": ("public/service/additive-manufacturing/resources/onto/admin/nodes/delete/<str:nodeID>/",onto.onto_deleteNode),
    #"orga_getPrinters": ("public/orga/getPrinters/",resources.orga_getPrinters),
    #"orga_addPrinter": ("public/orga/addPrinter/",resources.orga_addPrinter),
    #"orga_addPrinterEdit": ("public/orga/addPrinterEdit/",resources.orga_addPrinterEdit),
    #"orga_createPrinter": ("public/orga/createPrinter/",resources.orga_createPrinter),
    #"orga_removePrinter": ("public/orga/removePrinter/",resources.orga_removePrinter),
    #"orga_getMaterials": ("public/orga/getMaterials/",resources.orga_getMaterials),
    #"orga_addMaterial": ("public/orga/addMaterial/",resources.orga_addMaterial),
    #"orga_addMaterialEdit": ("public/orga/addMaterialEdit/",resources.orga_addMaterialEdit),
    #"orga_createMaterial": ("public/orga/createMaterial/",resources.orga_createMaterial),
    #"orga_removeMaterial": ("public/orga/removeMaterial/",resources.orga_removeMaterial),
    "orga_getResources": ("public/service/additive-manufacturing/resources/orga/get/", orga.orga_getResources),
    "orga_getNodes": ("public/service/additive-manufacturing/resources/orga/nodes/get/by-type/<str:resourceType>/",orga.orga_getNodes),
    "orga_getNodeViaID": ("public/service/additive-manufacturing/resources/orga/nodes/get/by-id/<str:nodeID>/", orga.orga_getNodeViaID),
    "orga_getAssociatedResources": ("public/service/additive-manufacturing/resources/orga/nodes/neighbors/get/<str:nodeID>/<str:resourceType>/", orga.orga_getAssociatedResources),
    "orga_createNode": ("public/service/additive-manufacturing/resources/orga/nodes/create/", orga.orga_createNode),
    "orga_updateNode": ("public/service/additive-manufacturing/resources/orga/nodes/update/", orga.orga_updateNode),
    "orga_deleteNode": ("public/service/additive-manufacturing/resources/orga/nodes/delete/<str:nodeID>/", orga.orga_deleteNode),
    "orga_addLinksToOrga": ("public/service/additive-manufacturing/resources/orga/edge/create/", orga.orga_addEdgesToOrga),
    "orga_addEdgeForOrga": ("public/service/additive-manufacturing/resources/orga/edge/update/", orga.orga_addEdgeForOrga),
    #"orga_updateLinkFromPrinterToMaterial": ("public/service/additive-manufacturing/resources/orga/link/patch/", resources.orga_updateMaterialAndPrinter),
    "orga_removeLink": ("public/service/additive-manufacturing/resources/orga/edge/delete/<str:entityID>/", orga.orga_removeEdge),
    "orga_deleteAllFromOrga": ("public/service/additive-manufacturing/resources/orga/edge/all/delete/", orga.orga_removeAll)

}

# add paths
for entry in newPaths:
    key = entry
    pathTuple = newPaths[entry]
    pathItself = pathTuple[0]
    handler = pathTuple[1]
    urlpatterns.append(path(pathItself, handler, name=key))

paths.update(newPaths)