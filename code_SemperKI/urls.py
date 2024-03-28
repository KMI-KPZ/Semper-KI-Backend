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
from django.conf import settings
from Generic_Backend.code_General.urls import paths, urlpatterns

##############################################################################
### WSGI

from .handlers import projectAndProcessManagement, testResponse, frontpage, sparqlQueries, files, admin, manageServices
from MSQ.handlers import interface


newPaths= {

    "getContractors": ("public/getContractors/<processID>/",projectAndProcessManagement.getContractors),
    
    "saveProjects": ("public/saveProjects/",projectAndProcessManagement.saveProjects),
    "retrieveProjects": ("public/retrieveProjects/",projectAndProcessManagement.retrieveProjects),
    "getMissedEvents": ("public/getMissedEvents/",projectAndProcessManagement.getMissedEvents),
    "getFlatProjects": ("public/getFlatProjects/",projectAndProcessManagement.getFlatProjects),
    "createProjectID": ("public/createProjectID/",projectAndProcessManagement.createProjectID),
    "getProject": ("public/getProject/<projectID>/",projectAndProcessManagement.getProject),
    "createProcessID": ("public/createProcessID/<projectID>/",projectAndProcessManagement.createProcessID),
    "updateProcess": ("public/updateProcess/",projectAndProcessManagement.updateProcess),
    "updateProject": ("public/updateProject/",projectAndProcessManagement.updateProject),
    "deleteProcesses": ("public/deleteProcesses/<projectID>/",projectAndProcessManagement.deleteProcesses),
    "deleteProjects": ("public/deleteProjects/",projectAndProcessManagement.deleteProjects),
    #"verifyProject": ("public/verifyProject/",projectAndProcessManagement.verifyProject),
    #"sendProject": ("public/sendProject/",projectAndProcessManagement.sendProject),
    "getProcessHistory": ("public/getProcessHistory/<processID>/",projectAndProcessManagement.getProcessHistory),
    "statusButtonRequest": ("public/statusButtonRequest/",projectAndProcessManagement.statusButtonRequest),

    "getServices": ("public/getServices/",manageServices.getServices),

    "getAllProjectsFlatAsAdmin": ("public/admin/getAllProjectsFlatAsAdmin/",admin.getAllProjectsFlatAsAdmin),
    "getSpecificProjectAsAdmin": ("public/admin/getSpecificProjectAsAdmin/<projectID>/",admin.getSpecificProjectAsAdmin),

    "isMagazineUp": ("public/isMagazineUp/",testResponse.isMagazineUp),

    "testQuery": ("private/testquery/",sparqlQueries.sendTestQuery),
    "sendQuery": ("private/sendQuery/",sparqlQueries.sendQuery),
    "testQuerySize": ("private/query/",frontpage.sparqlPage),
    "testCoypu": ("public/coypu/",sparqlQueries.sendQueryCoypu),

    "uploadFiles": ("public/uploadFiles/",files.uploadFiles),
    #"downloadFile": ("public/downloadFile/<processID>/<fileID>/",files.downloadFile),
    "downloadFile": ("public/downloadFile/<processID>/<fileID>/",files.downloadFileStream),
    "downloadFilesAsZip": ("public/downloadFilesAsZip/<processID>/",files.downloadFilesAsZip),
    "deleteFile": ("public/deleteFile/<processID>/<fileID>/",files.deleteFile),
    "downloadProcessHistory": ("public/downloadProcessHistory/<processID>/",files.downloadProcessHistory),

    #"getResultsBack": ("public/getResults/<taskID>/", interface.getResultsBack),
    "getResultsBackLocal": ("private/getResultsLocal/<taskID>/", interface.getResultsBack),
    #"sendRemote": ("private/sendRemote/", interface.sendExampleRemote),
    "sendLocal": ("private/sendLocal/", interface.sendExampleLocal),
    "getStateMachine": ("private/getStateMachine/", projectAndProcessManagement.getStateMachine),
}

# add paths
for entry in newPaths:
    key = entry
    pathTuple = newPaths[entry]
    pathItself = pathTuple[0]
    handler = pathTuple[1]
    urlpatterns.append(path(pathItself, handler, name=key))

paths.update(newPaths)


