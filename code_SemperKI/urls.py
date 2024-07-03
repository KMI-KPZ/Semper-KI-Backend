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

from .handlers import frontpage
from .handlers.public import admin, files, project, process, statemachine, miscellaneous, events
from .handlers.private import testResponse
from MSQ.handlers import interface

newPaths= {
    #"rest-test": ("public/resttest/<str:dummy>/", testResponse.restTest),
    #"rest-test2": ("public/resttest2/<str:dummy>/", testResponse.restTestAPI.as_view()),
    "schema": ('private/schema/', SpectacularAPIView.as_view(api_version='0.3')),
    "swagger-ui": ('private/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema')),
    
    "createProjectID": ('public/createProjectID/', project.createProjectID), 
    "getProject": ("public/getProject/<str:projectID>/",project.getProject),
    "getFlatProjects": ("public/getFlatProjects/", project.getFlatProjects),
    "updateProject": ("public/updateProject/" ,project.updateProject),
    "deleteProjects": ("public/deleteProjects/" ,project.deleteProjects),
    "saveProjects": ("public/saveProjects/", project.saveProjects),

    "getProcess": ("public/getProcess/<str:projectID>/<str:processID>/", process.getProcess),
    "createProcessID": ("public/createProcessID/<str:projectID>", process.createProcessID),
    "updateProcess": ("public/updateProcess/", process.updateProcess), 
    "deleteProcesses": ("public/deleteProcesses/<str:projectID>/", process.deleteProcesses), 
    "getProcessHistory": ("public/getProcessHistory/<str:processID>/", process.getProcessHistory),
    "getContractors": ("public/getContractors/<str:processID>/", process.getContractors),

    "getStateMachine": ("private/getStateMachine/", statemachine.getStateMachine), 
    "statusButtonRequest": ("public/statusButtonRequest/", statemachine.statusButtonRequest), 

    "getServices": ("public/getServices/", miscellaneous.getServices), 
    "getMissedEvents": ("public/getMissedEvents/", events.getMissedEvents),

    "uploadFiles": ("public/uploadFiles/",files.uploadFiles),
    "downloadFile": ("public/downloadFile/<str:projectID>/<str:processID>/<str:fileID>/", files.downloadFileStream),
    "downloadFilesAsZip": ("public/downloadFilesAsZip/<str:projectID>/<str:processID>/",files.downloadFilesAsZip), 
    "deleteFile": ("public/deleteFile/<str:projectID>/<str:processID>/<str:fileID>/",files.deleteFile), 
    "downloadProcessHistory": ("public/downloadProcessHistory/<str:processID>/", files.downloadProcessHistory), 

    "getAllProjectsFlatAsAdmin": ("public/admin/getAllProjectsFlatAsAdmin/",admin.getAllProjectsFlatAsAdmin),
    "getSpecificProjectAsAdmin": ("public/admin/getSpecificProjectAsAdmin/<str:projectID>/",admin.getSpecificProjectAsAdmin),

    #"isMagazineUp": ("public/isMagazineUp/",testResponse.isMagazineUp),

    "uploadFiles": ("public/uploadFiles/",files.uploadFiles),
    #"downloadFile": ("public/downloadFile/<processID>/<fileID>/",files.downloadFile),
    "downloadFile": ("public/downloadFile/<str:projectID>/<str:processID>/<str:fileID>/",files.downloadFileStream),
    "downloadFilesAsZip": ("public/downloadFilesAsZip/<str:projectID>/<str:processID>/",files.downloadFilesAsZip),
    "deleteFile": ("public/deleteFile/<str:projectID>/<str:processID>/<str:fileID>/",files.deleteFile),
    "downloadProcessHistory": ("public/downloadProcessHistory/<str:projectID>/<str:processID>/",files.downloadProcessHistory),

    #"getResultsBack": ("public/getResults/<taskID>/", interface.getResultsBack),
    "getResultsBackLocal": ("private/getResultsLocal/<str:taskID>/", interface.getResultsBack),
    #"sendRemote": ("private/sendRemote/", interface.sendExampleRemote),
    "sendLocal": ("private/sendLocal/", interface.sendExampleLocal), 
    
}

# add paths
for entry in newPaths:
    key = entry
    pathTuple = newPaths[entry]
    pathItself = pathTuple[0]
    handler = pathTuple[1]
    urlpatterns.append(path(pathItself, handler, name=key))

paths.update(newPaths)
