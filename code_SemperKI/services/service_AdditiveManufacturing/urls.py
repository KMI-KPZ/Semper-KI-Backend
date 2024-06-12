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

from .handlers import filter, resources
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
    "deletePostProcessing": ('public/service/additive-manufacturing/post-processing/delete/<str:projectID>/<str:processID>/<str:materialID>/',postProcessings.deletePostProcessingFromSelection),

    "uploadModel": ("public/service/additive-manufacturing/model/upload/",model.uploadModels),
    "deleteModel": ("public/service/additive-manufacturing/model/delete/<str:projectID>/<str:processID>/<str:fileID>/",model.deleteModel),
    "remeshSTLToTetraheadras": ("public/service/additive-manufacturing/model/remeshSTLToTetraheadras/<str:projectID>/<str:processID>/<str:fileID>/", model.remeshSTLToTetraheadras),
    "getModelRepository": ("public/service/additive-manufacturing/model/repository/", model.getModelRepository),

    #"checkPrintability": ("public/checkPrintability/",checkService.),
    #"checkPrices": ("public/checkPrices/",checkService.checkPrice),
    #"checkLogistics": ("public/checkLogistics/",checkService.checkLogistics),
    "checkModel": ("public/checkModel/<str:projectID>/<str:processID>/<str:fileID>/", checkService.checkModel),
    #"checkModelTest": ("public/checkModelTest/", checkService.getChemnitzData),

    "onto_getPrinters": ("public/onto/getPrinters/",resources.onto_getPrinters),
    "onto_getPrinter": ("public/onto/getPrinter/",resources.onto_getPrinter),
    "onto_getMaterials": ("public/onto/getMaterials/",resources.onto_getMaterials),
    "onto_getMaterial": ("public/onto/getMaterial/",resources.onto_getMaterial),
    "orga_getPrinters": ("public/orga/getPrinters/",resources.orga_getPrinters),
    "orga_addPrinter": ("public/orga/addPrinter/",resources.orga_addPrinter),
    "orga_addPrinterEdit": ("public/orga/addPrinterEdit/",resources.orga_addPrinterEdit),
    "orga_createPrinter": ("public/orga/createPrinter/",resources.orga_createPrinter),
    "orga_removePrinter": ("public/orga/removePrinter/",resources.orga_removePrinter),
    "orga_getMaterials": ("public/orga/getMaterials/",resources.orga_getMaterials),
    "orga_addMaterial": ("public/orga/addMaterial/",resources.orga_addMaterial),
    "orga_addMaterialEdit": ("public/orga/addMaterialEdit/",resources.orga_addMaterialEdit),
    "orga_createMaterial": ("public/orga/createMaterial/",resources.orga_createMaterial),
    "orga_removeMaterial": ("public/orga/removeMaterial/",resources.orga_removeMaterial),
}

# add paths
for entry in newPaths:
    key = entry
    pathTuple = newPaths[entry]
    pathItself = pathTuple[0]
    handler = pathTuple[1]
    urlpatterns.append(path(pathItself, handler, name=key))

paths.update(newPaths)