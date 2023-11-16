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

##############################################################################
### WSGI

from .handlers import projectAndProcessManagement, testResponse, frontpage, sparqlQueries, files, admin

paths_SemperKI = {

    "getContractors": "public/getContractors/",
    
    "saveProjects": "public/saveProjects/",
    "retrieveProjects": "public/retrieveProjects/",
    "getMissedEvents": "public/getMissedEvents/",
    "getFlatProjects": "public/getFlatProjects/",
    "createProjectID": "public/createProjectID/",
    "getProject": "public/getProject/<projectID>/",
    "createProcessID": "public/createProcessID/<projectID>/",
    "updateProcess": "public/updateProcess/",
    "updateProject": "public/updateProject/",
    "deleteProcess": "public/deleteProcess/<projectID>/",
    "deleteProject": "public/deleteProject/<projectID>/",
    "verifyProject": "public/verifyProject/",
    "sendProject": "public/sendProject/",

    "getAllProjectsFlatAsAdmin": "public/admin/getAllProjectsFlatAsAdmin/",
    "getSpecificProjectAsAdmin": "public/admin/getSpecificProjectAsAdmin/<projectID>/",

    "isMagazineUp": "public/isMagazineUp/",

    "testQuery": "private/testquery/",
    "sendQuery": "private/sendQuery/",
    "testQuerySize": "private/query/",
    "testCoypu": "public/coypu/",

    "testRedis": "private/testRedis/",
    "uploadModel": "public/uploadModel/",
    "uploadFiles": "public/uploadFiles/",
    "retrieveFilesTEST": "private/retrieveFiles/",
    "downloadFile": "public/downloadFile/<processID>/<fileID>",
    "downloadFilesAsZip": "public/downloadFilesAsZip/<processID>",
    "deleteFile": "public/deleteFile/<processID>/<fileID>",

}

# The name must remain "oath" as the content is included in the urls.py in code_General
urlpatterns_SemperKI = [
    path(paths["getMissedEvents"], projectAndProcessManagement.getMissedEvents, name='getMissedEvents'),
    path(paths["getFlatProjects"], projectAndProcessManagement.getFlatProjects, name="getFlatProjects"),
    path(paths["retrieveProjects"], projectAndProcessManagement.retrieveProjects, name='retrieveProjects'),
    path(paths["createProjectID"], projectAndProcessManagement.createProjectID, name="createProjectID"),
    path(paths["createProcessID"], projectAndProcessManagement.createProcessID, name="createProcessID"),
    path(paths["getProject"], projectAndProcessManagement.getProject, name="getProject"),
    path(paths["saveProjects"], projectAndProcessManagement.saveProjects, name='saveProjects'),
    path(paths["updateProcess"], projectAndProcessManagement.updateProcess, name='updateProcess'),
    path(paths["updateProject"], projectAndProcessManagement.updateProject, name='updateProject'),
    path(paths["deleteProcess"], projectAndProcessManagement.deleteProcess, name='deleteProcess'),
    path(paths["deleteProject"], projectAndProcessManagement.deleteProject, name='deleteProject'),
    path(paths["getContractors"], projectAndProcessManagement.getContractors, name='getContractors'),
    path(paths["verifyProject"], projectAndProcessManagement.verifyProject, name="verifyProject"),
    path(paths["sendProject"], projectAndProcessManagement.sendProject, name="sendProject"),

    path(paths["getAllProjectsFlatAsAdmin"], admin.getAllProjectsFlatAsAdmin, name="getAllProjectsFlatAsAdmin"),
    path(paths["getSpecificProjectAsAdmin"], admin.getSpecificProjectAsAdmin, name="getSpecificProjectAsAdmin"),

    path(paths["isMagazineUp"], testResponse.isMagazineUp, name="isMagazineUp"),

    path(paths["testQuery"], sparqlQueries.sendTestQuery, name="testQuery"),
    path(paths["testQuerySize"], frontpage.sparqlPage, name="testQueryPage"),
    path(paths["sendQuery"], sparqlQueries.sendQuery, name="sendQuery"),
    path(paths["testCoypu"], sparqlQueries.sendQueryCoypu, name="Coypu"),
    
    #path(paths["testRedis"], files.testRedis, name="testRedis"),
    path(paths["uploadModel"], files.uploadModel, name="uploadModel"),
    path(paths["uploadFiles"], files.uploadFiles, name="uploadFiles"),
    #path(paths["retrieveFilesTEST"], files.testGetUploadedFiles, name="getUploadedFiles"),
    path(paths["downloadFile"], files.downloadFile, name="downloadFile"),
    path(paths["downloadFilesAsZip"], files.downloadFilesAsZip, name="downloadFilesAsZip"),
    path(paths["deleteFile"], files.deleteFile, name="deleteFile"),

    
] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 



