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

from .handlers import projectAndProcessManagement, testResponse, frontpage, sparqlQueries, files, admin, manageServices
from .handlers.public import project, process, statemachine, miscellaneous, admin_, events
from MSQ.handlers import interface

newPaths= {
    #"rest-test": ("public/resttest/<str:dummy>/", testResponse.restTest),
    #"rest-test2": ("public/resttest2/<str:dummy>/", testResponse.restTestAPI.as_view()),
    "schema": ('api/schema/', SpectacularAPIView.as_view(api_version='v1')),
    "swagger-ui": ('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema')),
    
    "createProject": ('public/project/create/', project.createProjectID), #w
    "getProject": ("public/project/get/<str:projectID>/",project.getProject), #w
    "getFlatProjects": ("public/project/getFlat/", project.getFlatProjects), #w
    "updateProject": ("public/project/update/",project.updateProject), #w
    "deleteProjects": ("public/project/delete/",project.deleteProjects), #nw
    "saveProjects": ("public/project/saveProjects/", project.saveProjects), #nw
    "getProcess": ("public/process/getProcess/<str:projectID>/<str:processID>/", process.getProcess), #w
    "createProcessID": ("public/process/createProcessID/<str:projectID>", process.createProcessID), #w
    "updateProcess": ("public/process/updateProcess/", process.updateProcess), #nw
    "deleteProcesses": ("public/process/deleteProcesses/<str:projectID>/", process.deleteProcesses), #nw
    "getProcessHistory": ("public/process/getProcessHistory/<str:processID>/", process.getProcessHistory), #nw
    "getContractors": ("public/process/getContractors/<str:processID>", process.getContractors), #nw
    "getStateMachine": ("public/statemachine/getStateMachine/", statemachine.getStateMachine), #w
    "getServices": ("public/miscellaneous/getServices/", miscellaneous.getServices), #nw
    "getMissedEvents": ("public/events/getMissedEvents/", events.getMissedEvents), #nw
    "uploadFiles": ("public/miscellaneous/uploadFiles/",miscellaneous.uploadFiles), #nw
    "downloadFile": ("public/miscellaneous/downloadFile/<str:projectID>/<str:processID>/<str:fileID>/", miscellaneous.downloadFileStream), #nw
    "downloadFilesAsZip": ("public/miscellaneous/downloadFilesAsZip/<str:projectID>/<str:processID>/",miscellaneous.downloadFilesAsZip), #nw
    "deleteFile": ("public/miscellaneous/deleteFile/<str:projectID>/<str:processID>/<str:fileID>/",miscellaneous.deleteFile),   #nw
    "downloadProcessHistory": ("public/miscellaneous/downloadProcessHistory/<str:processID>/", miscellaneous.downloadProcessHistory), #nw
    "getAllProjectsFlatAsAdmin": ("public/admin_/getAllProjectsFlatAsAdmin/", admin_.getAllProjectsFlatAsAdmin), #nw
    "getSpecificProjectAsAdmin": ("public/admin_/getSpecificProjectAsAdmin/<str:projectID>/", admin_.getSpecificProjectAsAdmin), #nw
    "statusButtonRequest": ("public/miscellaneous/statusButtonRequest/", miscellaneous.statusButtonRequest), #nw


    "isMagazineUp": ("public/isMagazineUp/",testResponse.isMagazineUp),
     "testQuery": ("private/testquery/",sparqlQueries.sendTestQuery),
    "sendQuery": ("private/sendQuery/",sparqlQueries.sendQuery),
    "testQuerySize": ("private/query/",frontpage.sparqlPage),
    "testCoypu": ("public/coypu/",sparqlQueries.sendQueryCoypu),

    #"getResultsBack": ("public/getResults/<taskID>/", interface.getResultsBack),
    "getResultsBackLocal": ("private/getResultsLocal/<str:taskID>/", interface.getResultsBack), #nw
    #"sendRemote": ("private/sendRemote/", interface.sendExampleRemote),
    "sendLocal": ("private/sendLocal/", interface.sendExampleLocal), #nw
    
}

# add paths
for entry in newPaths:
    key = entry
    pathTuple = newPaths[entry]
    pathItself = pathTuple[0]
    handler = pathTuple[1]
    urlpatterns.append(path(pathItself, handler, name=key))

paths.update(newPaths)


