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

from .handlers.public.resources import orga, onto, kgDBAM, pdfPipeline, verification, colors
from .handlers.public import materials, checkService, filter, model, postProcessings, costs

from code_SemperKI.urls import paths, urlpatterns


newPaths = {
    #"getProcessData": ('public/getProcessData/',filter.getProcessData),
    #"getModels": ('public/getModels/',filter.getModels),
    
    "getFilters": ("public/service/additive-manufacturing/filters/get/", filter.getFilters),

    "getMaterials": ('public/service/additive-manufacturing/material/get/',materials.retrieveMaterialsWithFilter),
    "setMaterial": ('public/service/additive-manufacturing/material/set/',materials.setMaterialSelection),
    "deleteMaterial": ('public/service/additive-manufacturing/material/delete/<str:projectID>/<str:processID>/<int:groupID>/',materials.deleteMaterialFromSelection),

    "getPostProcessings": ('public/service/additive-manufacturing/post-processing/get/',postProcessings.retrievePostProcessingsWithFilter),
    "setPostProcessing": ('public/service/additive-manufacturing/post-processing/set/',postProcessings.setPostProcessingSelection),
    "deletePostProcessing": ('public/service/additive-manufacturing/post-processing/delete/<str:projectID>/<str:processID>/<int:groupID>/<str:postProcessingID>/',postProcessings.deletePostProcessingFromSelection),

    "uploadModel": ("public/service/additive-manufacturing/model/upload/",model.uploadModels),
    "uploadModelWithoutFile": ("public/service/additive-manufacturing/model/upload-wo-file/", model.uploadModelWithoutFile),
    "updateModel": ("public/service/additive-manufacturing/model/update/", model.updateModel),
    "deleteModel": ("public/service/additive-manufacturing/model/delete/<str:projectID>/<str:processID>/<int:groupID>/<str:fileID>/",model.deleteModel),
    "checkModel": ("public/service/additive-manufacturing/model/check/<str:projectID>/<str:processID>/<str:fileID>/", model.checkModel),
    #"remeshSTLToTetraheadras": ("public/service/additive-manufacturing/model/remeshSTLToTetraheadras/<str:projectID>/<str:processID>/<str:fileID>/", model.remeshSTLToTetraheadras),
    "getModelRepository": ("public/service/additive-manufacturing/model/repository/get/", model.getModelRepository),

    #"checkPrintability": ("public/checkPrintability/",checkService.),
    #"checkPrices": ("public/checkPrices/",checkService.checkPrice),
    #"checkLogistics": ("public/checkLogistics/",checkService.checkLogistics),
    
    #"checkModelTest": ("public/checkModelTest/", checkService.getChemnitzData),
    "getVerificationForOrganization": ("public/service/additive-manufacturing/verification/get/", verification.getVerificationForOrganization),
    "createVerificationForOrganization": ("public/service/additive-manufacturing/verification/create/", verification.createVerificationForOrganization),
    "updateVerificationForOrganization": ("public/service/additive-manufacturing/verification/update/", verification.updateVerificationForOrganization),
    "deleteVerificationForOrganization": ("public/service/additive-manufacturing/verification/delete/<str:printerID>/<str:materialID>/", verification.deleteVerificationForOrganization),


    "getPropertyDefinitionFrontend": ("public/service/additive-manufacturing/resources/onto/nodes/properties/get/by-type/<str:nodeType>/", kgDBAM.getPropertyDefinitionFrontend),
    
    "getRALList": ("public/service/additive-manufacturing/resources/colors/getRALList/", colors.getRALList),
    #"setColor": ("public/service/additive-manufacturing/resources/colors/set/", colors.setColor),

    "onto_getGraph": ("public/service/additive-manufacturing/resources/onto/admin/graph/get/", onto.onto_getGraph),
    "onto_getResources": ("public/service/additive-manufacturing/resources/onto/admin/nodes/by-type/get/<str:resourceType>/",onto.onto_getResources),
    "onto_getNodeViaID": ("public/service/additive-manufacturing/resources/onto/admin/nodes/by-id/get/<str:nodeID>/", onto.onto_getNodeViaID),
    "onto_getAssociatedResources": ("public/service/additive-manufacturing/resources/onto/admin/nodes/neighbors/get/<str:nodeID>/<str:resourceType>/", onto.onto_getAssociatedResources),
    "onto_getNeighbors": ("public/service/additive-manufacturing/resources/onto/admin/nodes/neighbors/all/get/<str:nodeID>/", onto.onto_getNeighbors),
    "onto_addEdge": ("public/service/additive-manufacturing/resources/onto/admin/edge/create/",onto.onto_addEdge),
    "onto_createOrUpdateAndLinkNodes": ("public/service/additive-manufacturing/resources/onto/admin/nodes/create-and-link/", onto.onto_createOrUpdateAndLinkNodes),
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
    "orga_getGraph": ("public/service/additive-manufacturing/resources/orga/graph/get/", orga.orga_getGraph),
    "orga_getResources": ("public/service/additive-manufacturing/resources/orga/nodes/all/get/", orga.orga_getResources),
    "orga_getNodes": ("public/service/additive-manufacturing/resources/orga/nodes/by-type/get/<str:resourceType>/",orga.orga_getNodes),
    "orga_getNodeViaID": ("public/service/additive-manufacturing/resources/orga/nodes/by-id/get/<str:nodeID>/", orga.orga_getNodeViaID),
    "orga_getAssociatedResources": ("public/service/additive-manufacturing/resources/orga/nodes/neighbors/by-type/get/<str:nodeID>/<str:resourceType>/", orga.orga_getAssociatedResources),
    "orga_getNeighbors": ("public/service/additive-manufacturing/resources/orga/nodes/neighbors/all/get/<str:nodeID>/", orga.orga_getNeighbors),
    "orga_createNode": ("public/service/additive-manufacturing/resources/orga/nodes/create/", orga.orga_createNode),
    "orga_updateNode": ("public/service/additive-manufacturing/resources/orga/nodes/update/", orga.orga_updateNode),
    "orga_deleteNode": ("public/service/additive-manufacturing/resources/orga/nodes/delete/<str:nodeID>/", orga.orga_deleteNode),
    "orga_addLinksToOrga": ("public/service/additive-manufacturing/resources/orga/edge/to-orga/create/", orga.orga_addEdgesToOrga),
    "orga_addEdgeForOrga": ("public/service/additive-manufacturing/resources/orga/edge/between-entities/create/", orga.orga_addEdgeForOrga),
    "orga_createOrUpdateAndLinkNodes": ("public/service/additive-manufacturing/resources/orga/nodes/create-and-link/", orga.orga_createOrUpdateAndLinkNodes),
    "orga_removeLink": ("public/service/additive-manufacturing/resources/orga/edge/between-entities/delete/<str:entity1ID>/<str:entity2ID>/", orga.orga_removeEdge),
    "orga_deleteLinkToOrga": ("public/service/additive-manufacturing/resources/orga/edge/to-orga/delete/<str:entityID>/", orga.orga_removeEdgeToOrga),
    "orga_deleteAllFromOrga": ("public/service/additive-manufacturing/resources/orga/edge/all/delete/", orga.orga_removeAll),
    "orga_getRequestsForAdditions": ("public/service/additive-manufacturing/resources/orga/request/get/", orga.orga_getRequestsForAdditions),
    "orga_makeRequestForAdditions": ("public/service/additive-manufacturing/resources/orga/request/post/", orga.orga_makeRequestForAdditions),
    "orga_cloneTestGraphToOrgaForTests": ("private/service/additive-manufacturing/resources/orga/cloneTestGraphToOrgaForTests/", orga.cloneTestGraphToOrgaForTests),

    ########################
    "apiExtractPDFs": ("public/api/extractFromPDF/", pdfPipeline.extractFromPDF),
    "apiExtractPDFsTest": ("public/api/extractFromJSON/", pdfPipeline.extractFromJSON),
    "loadInitGraphViaAPI": ("public/api/graph/loadInitGraph/", kgDBAM.loadInitGraphViaAPI),
    "apiCalculateCosts": ("public/api/calculateCosts/", costs.apiCalculateCosts),
    "apiOnto_getGraph": ("public/api/service/additive-manufacturing/resources/onto/admin/graph/get/", onto.onto_getGraph),
    "apiOnto_getResources": ("public/api/service/additive-manufacturing/resources/onto/admin/nodes/by-type/get/<str:resourceType>/",onto.onto_getResources),
    "apiOnto_getNodeViaID": ("public/api/service/additive-manufacturing/resources/onto/admin/nodes/by-id/get/<str:nodeID>/", onto.onto_getNodeViaID),
    "apiOnto_getAssociatedResources": ("public/api/service/additive-manufacturing/resources/onto/admin/nodes/neighbors/get/<str:nodeID>/<str:resourceType>/", onto.onto_getAssociatedResources),
    "apiOnto_getNeighbors": ("public/api/service/additive-manufacturing/resources/onto/admin/nodes/neighbors/all/get/<str:nodeID>/", onto.onto_getNeighbors),
    "apiOnto_addEdge": ("public/api/service/additive-manufacturing/resources/onto/admin/edge/create/",onto.onto_addEdge),
    "apiOnto_createOrUpdateAndLinkNodes": ("public/api/service/additive-manufacturing/resources/onto/admin/nodes/create-and-link/", onto.onto_createOrUpdateAndLinkNodes),
    "apiOnto_removeEdge": ("public/api/service/additive-manufacturing/resources/onto/admin/edge/delete/<str:entity1ID>/<str:entity2ID>/",onto.onto_removeEdge),
    "apiOnto_addNode": ("public/api/service/additive-manufacturing/resources/onto/admin/nodes/create/",onto.onto_addNode),
    "apiOnto_updateNode": ("public/api/service/additive-manufacturing/resources/onto/admin/nodes/update/",onto.onto_updateNode),
    "apiOnto_deleteNode": ("public/api/service/additive-manufacturing/resources/onto/admin/nodes/delete/<str:nodeID>/",onto.onto_deleteNode),
    
}

# add paths
for entry in newPaths:
    key = entry
    pathTuple = newPaths[entry]
    pathItself = pathTuple[0]
    handler = pathTuple[1]
    urlpatterns.append(path(pathItself, handler, name=key))

paths.update(newPaths)