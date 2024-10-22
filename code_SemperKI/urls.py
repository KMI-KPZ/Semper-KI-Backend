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

from django.urls import path, include
from django.conf import settings
from Generic_Backend.code_General.urls import paths, urlpatterns

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

##############################################################################
### WSGI

from .handlers.public import admin, files, project, process, statemachine, miscellaneous, events, pdfPipeline
from .handlers.private import testResponse, knowledgeGraphDB
from MSQ.handlers import interface

newPaths= {
    #"rest-test": ("public/resttest/<str:dummy>/", testResponse.restTest),
    #"rest-test2": ("public/resttest2/<str:dummy>/", testResponse.restTestAPI.as_view()),
    #"schema": ('private/schema/', SpectacularAPIView.as_view(api_version='0.3')),
    #"swagger-ui": ('private/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema')),
    
    "createProjectID": ('public/project/create/', project.createProjectID), 
    "getProject": ("public/project/get/<str:projectID>/",project.getProject),
    "getFlatProjects": ("public/project/getFlat/", project.getFlatProjects),
    "updateProject": ("public/project/update/" ,project.updateProject),
    "deleteProjects": ("public/project/delete/" ,project.deleteProjects),
    "saveProjects": ("public/project/save/", project.saveProjects),

    "getProcess": ("public/process/get/<str:projectID>/<str:processID>/", process.getProcess),
    "createProcessID": ("public/process/create/<str:projectID>/", process.createProcessID),
    "updateProcess": ("public/process/update/", process.updateProcess), 
    "deleteProcesses": ("public/process/delete/<str:projectID>/", process.deleteProcesses), 
    "getProcessHistory": ("public/process/history/get/<str:processID>/", process.getProcessHistory),
    "getContractors": ("public/process/contractors/get/<str:processID>/", process.getContractors),

    "getStateMachine": ("private/states/machine/get/", statemachine.getStateMachine), 
    "statusButtonRequest": ("public/states/buttons/get/", statemachine.statusButtonRequest), 

    "getServices": ("public/services/get/", miscellaneous.getServices), 
    "getMissedEvents": ("public/events/missed/get/", events.getMissedEvents),
    "retrieveResultsFromQuestionnaire": ("public/questionnaire/retrieve/", miscellaneous.retrieveResultsFromQuestionnaire),

    "uploadFiles": ("public/files/upload/",files.uploadFiles),
    "downloadFile": ("public/files/download/file/<str:projectID>/<str:processID>/<str:fileID>/", files.downloadFileStream),
    "downloadFilesAsZip": ("public/files/download/zip/<str:projectID>/<str:processID>/",files.downloadFilesAsZip), 
    "deleteFile": ("public/files/delete/<str:projectID>/<str:processID>/<str:fileID>/",files.deleteFile), 
    "downloadProcessHistory": ("public/files/download/history/<str:processID>/", files.downloadProcessHistory), 

    "getAllProjectsFlatAsAdmin": ("public/admin/getAllProjectsFlatAsAdmin/",admin.getAllProjectsFlatAsAdmin),
    "getSpecificProjectAsAdmin": ("public/admin/getSpecificProjectAsAdmin/<str:projectID>/",admin.getSpecificProjectAsAdmin),

    "getNode": ("private/nodes/get/<str:nodeID>/", knowledgeGraphDB.getNode),
    "getNodesByType": ("private/nodes/get/by-type/<str:nodeType>/", knowledgeGraphDB.getNodesByType),
    "getNodesByProperty": ("private/nodes/get/by-property/<str:property>/", knowledgeGraphDB.getNodesByProperty),
    "createNode": ("private/nodes/create/", knowledgeGraphDB.createNode),
    "deleteNode": ("private/nodes/delete/<str:nodeID>/", knowledgeGraphDB.deleteNode),
    "updateNode": ("private/nodes/update/", knowledgeGraphDB.updateNode),
    "getEdgesForNode": ("private/edges/get/<str:nodeID>/", knowledgeGraphDB.getEdgesForNode),
    "getSpecificNeighborsByType": ("private/edges/get/by-type/<str:nodeID>/<str:nodeType>/", knowledgeGraphDB.getSpecificNeighborsByType),
    "getSpecificNeighborsByProperty": ("private/edges/get/by-property/<str:nodeID>/<str:property>/", knowledgeGraphDB.getSpecificNeighborsByProperty),
    "getNodesByTypeAndProperty": ("private/edges/get/by-property-and-type/<str:nodeType>/<str:nodeProperty>/<str:value>/", knowledgeGraphDB.getNodesByTypeAndProperty),
    "createEdge": ("private/edges/create/", knowledgeGraphDB.createEdge),
    "deleteEdge": ("private/edges/delete/<str:nodeID1>/<str:nodeID2>/", knowledgeGraphDB.deleteEdge),
    "getGraph": ("private/graph/get/for-backend/", knowledgeGraphDB.getGraph),
    "getGraphForFrontend": ("private/graph/get/", knowledgeGraphDB.getGraphForFrontend),
    "createGraph": ("private/graph/create/", knowledgeGraphDB.createGraph),
    "loadTestGraph": ("private/graph/loadTestGraph/", knowledgeGraphDB.loadTestGraph),
    "deleteGraph": ("private/graph/delete/", knowledgeGraphDB.deleteGraph),

    #"isMagazineUp": ("public/isMagazineUp/",testResponse.isMagazineUp),

    #"getResultsBack": ("public/getResults/<taskID>/", interface.getResultsBack),
    "getResultsBackLocal": ("private/getResultsLocal/<str:taskID>/", interface.getResultsBack),
    #"sendRemote": ("private/sendRemote/", interface.sendExampleRemote),
    "sendLocal": ("private/sendLocal/", interface.sendExampleLocal), 
    

    ########################## API ##############################
    "apiCreateProject": ("public/api/project/create/", project.createProjectID),
    "apiCreateProcess": ("public/api/process/create/<str:projectID>/", process.createProcessID),
    "apiExtractPDFs": ("public/api/extractFromPDF/", pdfPipeline.extractFromPDF),
}

# add paths
for entry in newPaths:
    key = entry
    pathTuple = newPaths[entry]
    pathItself = pathTuple[0]
    handler = pathTuple[1]
    urlpatterns.append(path(pathItself, handler, name=key))

paths.update(newPaths)
