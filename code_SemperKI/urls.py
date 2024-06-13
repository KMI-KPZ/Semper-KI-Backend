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

from .handlers import projectAndProcessManagement, testResponse, files, admin, manageServices
from .handlers.public import project
from MSQ.handlers import interface

newPaths= {
    #"rest-test": ("public/resttest/<str:dummy>/", testResponse.restTest),
    #"rest-test2": ("public/resttest2/<str:dummy>/", testResponse.restTestAPI.as_view()),
    "schema": ('api/schema/', SpectacularAPIView.as_view(api_version='0.3')),
    "swagger-ui": ('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema')),

    "createProject": ('public/project/create/', project.createProjectID),
    "getProject": ("public/project/get/<str:projectID>/",project.getProject),
    "getFlatProjects": ("public/project/getFlat/", project.getFlatProjects),
    "updateProject": ("public/project/update/",project.updateProject),
    "deleteProjects": ("public/project/delete/",project.deleteProjects),

    "getContractors": ("public/getContractors/<str:processID>/",projectAndProcessManagement.getContractors),
    "saveProjects": ("public/saveProjects/",projectAndProcessManagement.saveProjects),
    #"retrieveProjects": ("public/retrieveProjects/",projectAndProcessManagement.retrieveProjects),
    "getMissedEvents": ("public/getMissedEvents/",projectAndProcessManagement.getMissedEvents),
    #"createProjectID": ("public/createProjectID/",projectAndProcessManagement.createProjectID),
    #"getProject": ("public/getProject/<projectID>/",projectAndProcessManagement.getProject),
    #"getFlatProjects": ("public/getFlatProjects/", projectAndProcessManagement.getFlatProjects),
    "getProcess": ("public/getProcess/<projectID>/<processID>/",projectAndProcessManagement.getProcess),
    "createProcessID": ("public/createProcessID/<projectID>/",projectAndProcessManagement.createProcessID),
    "updateProcess": ("public/updateProcess/",projectAndProcessManagement.updateProcess),
    #"updateProject": ("public/updateProject/",projectAndProcessManagement.updateProject),
    "deleteProcesses": ("public/deleteProcesses/<projectID>/",projectAndProcessManagement.deleteProcesses),
    #"deleteProjects": ("public/deleteProjects/",projectAndProcessManagement.deleteProjects),
    #"verifyProject": ("public/verifyProject/",projectAndProcessManagement.verifyProject),
    #"sendProject": ("public/sendProject/",projectAndProcessManagement.sendProject),
    "getProcessHistory": ("public/getProcessHistory/<processID>/",projectAndProcessManagement.getProcessHistory),
    "statusButtonRequest": ("public/statusButtonRequest/",projectAndProcessManagement.statusButtonRequest),
    "getStateMachine": ("private/getStateMachine/", projectAndProcessManagement.getStateMachine),

    "getServices": ("public/getServices/",manageServices.getServices),

    "getAllProjectsFlatAsAdmin": ("public/admin/getAllProjectsFlatAsAdmin/",admin.getAllProjectsFlatAsAdmin),
    "getSpecificProjectAsAdmin": ("public/admin/getSpecificProjectAsAdmin/<projectID>/",admin.getSpecificProjectAsAdmin),

    "isMagazineUp": ("public/isMagazineUp/",testResponse.isMagazineUp),

    "uploadFiles": ("public/uploadFiles/",files.uploadFiles),
    #"downloadFile": ("public/downloadFile/<processID>/<fileID>/",files.downloadFile),
    "downloadFile": ("public/downloadFile/<projectID>/<processID>/<fileID>/",files.downloadFileStream),
    "downloadFilesAsZip": ("public/downloadFilesAsZip/<projectID>/<processID>/",files.downloadFilesAsZip),
    "deleteFile": ("public/deleteFile/<projectID>/<processID>/<fileID>/",files.deleteFile),
    "downloadProcessHistory": ("public/downloadProcessHistory/<projectID>/<processID>/",files.downloadProcessHistory),

    #"getResultsBack": ("public/getResults/<taskID>/", interface.getResultsBack),
    "getResultsBackLocal": ("private/getResultsLocal/<taskID>/", interface.getResultsBack),
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


