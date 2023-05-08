"""
Part of Semper-KI software

Silvio Weging 2023

Contains: backend_django URL Configuration

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
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings

##############################################################################
### WSGI

from .handlers import test_response, authentification, profiles, filter, frontpage, sparqlQueries, files, statistics, checkOrder, dashboard
from Benchy.BenchyMcMarkface import startFromDjango
from django.conf.urls.static import static

paths = {
    "landingPage": "",
    "test": 'public/test/',
    "csrfTest": 'public/testCsrf/',
    "csrfCookie": 'public/csrfCookie/',
    "login" : "public/login/",
    "logout": "public/logout/",
    "callback": "public/callback/",
    "getUser": "public/getUser/",
    "getProcessData": 'public/getProcessData/',
    "getFilters": 'public/getFilters/',
    "getModels": 'public/getModels/',
    "getMaterials": 'public/getMaterials/',
    "getPostProcessing": 'public/getPostProcessing/',
    "deleteUser": "public/profileDeleteUser/",
    "addUser": "private/profile_addUser/",
    "getUserTest": "private/profile_getUser/",
    "updateName": "public/updateName/",
    "updateRole": "public/updateRole/",
    "testQuery": "private/testquery/",
    "sendQuery": "private/sendQuery/",
    "testQuerySize": "private/query/",
    "isLoggedIn": "public/isLoggedIn/",
    "testRedis": "private/testRedis/",
    "uploadModels": "public/uploadModels/", #uploadModels uploadFiles
    "retrieveFilesTEST": "private/retrieveFiles/",
    "getDatabase" : "admin/getData/",
    "statistics": "public/getStatistics/",
    "benchyPage": "private/benchy/",
    "benchyMcMarkface": "private/benchyMcMarkface/",
    "getMaterials": "public/getMaterials/",
    "updateCart": "public/updateCart/",
    "getCart": "public/getCart/",
    "checkPrintability": "public/checkPrintability/",
    "checkPrices": "public/checkPrices/",
    "checkLogistics": "public/checkLogistics/",
    "sendOrder": "public/sendOrder/",
    "retrieveOrders": "public/getOrders/",
    "updateOrder": "public/updateOrder/",
    "getManufacturers": "public/getManufacturers/",
    "deleteOrder": "public/deleteOrder/",
    "deleteOrderCollection": "public/deleteOrderCollection/",
    "getMissedEvents": "public/getMissedEvents/",
    "getFileFromOrder": "public/getFileFromOrder/"
}

urlpatterns = [
    path(paths["landingPage"], frontpage.landingPage, name="landingPage"),
    path(paths["benchyPage"], frontpage.benchyPage, name="benchy"),
    path(paths["benchyMcMarkface"], startFromDjango, name="benchyMcMarkface"),

    re_path(r'^public/doc', frontpage.docPage, name="docPage"),

    path(paths["test"], test_response.testResponse, name='test_response'),
    path(paths["csrfTest"], test_response.testResponseCsrf, name='test_response_csrf'),
    path(paths["csrfCookie"], test_response.testResponseCsrf, name='test_response_csrf'),
    path('private/test/', test_response.testResponse, name='test_response'),
    path('private/testWebsocket/', test_response.testCallToWebsocket, name='testCallToWebsocket'),

    path(paths["login"], authentification.loginUser, name="loginUser"),
    path(paths["logout"], authentification.logoutUser, name="logoutUser"),
    path(paths["callback"], authentification.callbackLogin, name="callbackLogin"),
    path(paths["getUser"], authentification.getAuthInformation, name="getAuthInformation"),
    path(paths["isLoggedIn"], authentification.isLoggedIn, name="isLoggedIn"),

    path(paths["getProcessData"], filter.getProcessData, name='getProcessData'),
    path(paths["getModels"], filter.getModels, name='getModels'),
    path(paths["getFilters"], filter.getFilters, name='getFilters'),
    path(paths["getMaterials"], filter.getMaterials, name='getMaterials'),
    path(paths["getPostProcessing"], filter.getPostProcessing, name='getPostProcessing'),

    path(paths["updateCart"], checkOrder.updateCart, name='updateCart'),
    path(paths["getCart"], checkOrder.getCart, name='getCart'),
    path(paths["getManufacturers"], checkOrder.getManufacturers, name='getManufacturers'),
    path(paths["checkPrintability"], checkOrder.checkPrintability, name='checkPrintability'),
    path(paths["checkPrices"], checkOrder.checkPrice, name='checkPrice'),
    path(paths["checkLogistics"], checkOrder.checkLogistics, name='checkLogistics'),
    path(paths["sendOrder"], checkOrder.sendOrder, name='sendOrder'),

    path(paths["retrieveOrders"], dashboard.retrieveOrders, name='retrieveOrders'),
    path(paths["updateOrder"], dashboard.updateOrder, name='updateOrder'),
    path(paths["deleteOrder"], dashboard.deleteOrder, name='deleteOrder'),
    path(paths["deleteOrderCollection"], dashboard.deleteOrderCollection, name='deleteOrderCollection'),
    path(paths["getMissedEvents"], dashboard.getMissedEvents, name='getMissedEvents'),

    path(paths["deleteUser"], profiles.deleteUser, name="deleteUser"),
    #path("private/testDB/", profiles.checkConnection, name="checkConnection"),
    #path("private/createDB/", profiles.createTable, name="createTable"),
    #path("private/insertInDB/", profiles.insertUser, name="insertUser"),
    path(paths["addUser"], profiles.addUserTest, name="addUser"),
    path(paths["getUserTest"], profiles.getUserTest, name="getUserTest"),
    path(paths["updateName"], profiles.updateName, name="updateName"),
    #path(paths["updateRole"], profiles.updateRole, name="updateRole"),

    path(paths["testQuery"], sparqlQueries.sendQuery, name="testQuery"),
    path(paths["testQuerySize"], frontpage.sparqlPage, name="testQueryPage"),
    path(paths["sendQuery"], sparqlQueries.sendQuery, name="sendQuery"),
    
    path(paths["testRedis"], files.testRedis, name="testRedis"),
    path(paths["uploadModels"], files.uploadModels, name="uploadModels"),
    path(paths["retrieveFilesTEST"], files.testGetUploadedFiles, name="getUploadedFiles"),
    path(paths["getFileFromOrder"], files.downloadFiles, name="getFileFromOrder"),
    
    path(paths["statistics"], statistics.getNumberOfUsers, name="statistics")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 

urlpatterns.append(re_path(r'^.*', statistics.getIpAdress, name="everythingElse"))

##############################################################################
### ASGI
from .handlers.test_response import testWebSocket
from .handlers.websocket import GeneralWebSocket

websockets = [
    #path("ws/testWebsocket/", testWebSocket.as_asgi(), name="testAsync"),
    path("ws/generalWebsocket/", GeneralWebSocket.as_asgi(), name="Websocket")
]