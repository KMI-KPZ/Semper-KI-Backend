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

from .handlers import checkService, filter, resources, model

from code_SemperKI.urls import paths, urlpatterns

paths.update({
    "getProcessData": 'public/getProcessData/',
    "getModels": 'public/getModels/',
    "getFilters": 'public/getFilters/',
    "getMaterials": 'public/getMaterials/',
    "getPostProcessing": 'public/getPostProcessing/',

    "uploadModel": "public/uploadModel/",
    "deleteModel": "public/deleteModel/<processID>/",

    "checkPrintability": "public/checkPrintability/",
    "checkPrices": "public/checkPrices/",
    "checkLogistics": "public/checkLogistics/",

    "onto_getPrinters": "public/onto/getPrinters/",
    "onto_getPrinter": "public/onto/getPrinter/",
    "onto_getMaterials": "public/onto/getMaterials/",
    "onto_getMaterial": "public/onto/getMaterial/",
    "orga_getPrinters": "public/orga/getPrinters/",
    "orga_addPrinter": "public/orga/addPrinter/",
    "orga_addPrinterEdit": "public/orga/addPrinterEdit/",
    "orga_createPrinter": "public/orga/createPrinter/",
    "orga_removePrinter": "public/orga/removePrinter/",
    "orga_getMaterials": "public/orga/getMaterials/",
    "orga_addMaterial": "public/orga/addMaterial/",
    "orga_addMaterialEdit": "public/orga/addMaterial/",
    "orga_createMaterial": "public/orga/createMaterial/",
    "orga_removeMaterial": "public/orga/removeMaterial/",
})

urlpatterns.extend([

    path(paths["getProcessData"], filter.getProcessData, name='getProcessData'),
    path(paths["getModels"], filter.getModels, name='getModels'),
    path(paths["getFilters"], filter.getFilters, name='getFilters'),
    path(paths["getMaterials"], filter.getMaterials, name='getMaterials'),
    path(paths["getPostProcessing"], filter.getPostProcessing, name='getPostProcessing'),

    path(paths["uploadModel"], model.uploadModel, name="uploadModel"),
    path(paths["deleteModel"], model.deleteModel, name='deleteModel'),

    path(paths["checkPrintability"], checkService.checkPrintability, name='checkPrintability'),
    path(paths["checkPrices"], checkService.checkPrice, name='checkPrice'),
    path(paths["checkLogistics"], checkService.checkLogistics, name='checkLogistics'),

    path(paths["onto_getMaterials"], resources.onto_getMaterials, name="getMaterials"),
    path(paths["onto_getMaterial"], resources.onto_getMaterial, name="getMaterial"),
    path(paths["onto_getPrinters"], resources.onto_getPrinters, name="getPrinters"),
    path(paths["onto_getPrinter"], resources.onto_getPrinter, name="onto_getPrinter"),
    path(paths["orga_addPrinter"], resources.orga_addPrinter, name="orga_addPrinter"),
    path(paths["orga_addPrinterEdit"], resources.orga_addPrinterEdit, name="orga_addPrinterEdit"),
    path(paths["orga_createPrinter"], resources.orga_createPrinter, name="orga_createPrinter"),
    path(paths["orga_removePrinter"], resources.orga_removePrinter, name="orga_removePrinter"),
    path(paths["orga_getPrinters"], resources.orga_getPrinters, name="orga_getPrinters"),
    path(paths["orga_addMaterial"], resources.orga_addMaterial, name="orga_addMaterial"),
    path(paths["orga_addMaterialEdit"], resources.orga_addMaterialEdit, name="orga_addPrinterEdit"),
    path(paths["orga_createMaterial"], resources.orga_createMaterial, name="orga_createMaterial"),
    path(paths["orga_removeMaterial"], resources.orga_removeMaterial, name="orga_removeMaterial"),
    path(paths["orga_getMaterials"], resources.orga_getMaterials, name="orga_getMaterials"),
])