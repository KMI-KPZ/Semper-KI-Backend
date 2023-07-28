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

from .handlers import test_response, authentification, profiles, filter, frontpage, sparqlQueries, files, statistics, checkOrder, dashboard, organizations, ontology
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
    "getRoles": "public/getRoles/",
    "getPermissionsFile": "public/getPermissionMask/",
    "getPermissions": "public/getPermissions/",
    "getNewPermissions": "public/getNewPermissions/",
    "getProcessData": 'public/getProcessData/',
    "getFilters": 'public/getFilters/',
    "getModels": 'public/getModels/',
    "getMaterials": 'public/getMaterials/',
    "getPostProcessing": 'public/getPostProcessing/',
    "deleteUser": "public/profileDeleteUser/",
    "addUser": "private/profile_addUser/",
    "getUserTest": "private/profile_getUser/",
    "updateDetails": "public/updateDetails/",
    "updateDetailsOfOrga": "public/updateOrgaDetails",
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
    "getFileFromOrder": "public/getFileFromOrder/",
    "isMagazineUp": "public/isMagazineUp/",
    "organisations_addUser": "public/organizations/addUser/",
    "organisations_getInviteLink": "public/organizations/getInviteLink/",
    "organisations_fetchUsers": "public/organizations/fetchUsers/",
    "organisations_deleteUser": "public/organizations/deleteUser/",
    "organisations_createRole": "public/organizations/createRole/",
    "organisations_getRoles": "public/organizations/getRoles/",
    "organisations_assignRole": "public/organizations/assignRole/",
    "organisations_removeRole": "public/organizations/removeRole/",
    "organisations_editRole": "public/organizations/editRole/",
    "organisations_deleteRole": "public/organizations/deleteRole/",
    "organisations_getPermissions": "public/organizations/getPermissions/",
    "organisations_getPermissionsForRole": "public/organizations/getPermissionsForRole/",
    "organisations_setPermissionsForRole": "public/organizations/setPermissionsForRole/",
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
    "orga_removeMaterial": "public/orga/removeMaterial/"
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
    path(paths["getRoles"], authentification.getRolesOfUser, name="getRoles"),
    path(paths["getPermissions"], authentification.getPermissionsOfUser, name="getPermissions"),
    path(paths["getNewPermissions"], authentification.getNewRoleAndPermissionsForUser, name="getNewPermissions"),
    path(paths["getPermissionsFile"], authentification.provideRightsFile, name="getPermissionsFile"),

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
    path(paths["updateDetails"], profiles.updateDetails, name="updateDetails"),
    #path(paths["updateRole"], profiles.updateRole, name="updateRole"),

    path(paths["organisations_addUser"], organizations.organisations_addUser, name="organisations_addUser"),
    path(paths["organisations_fetchUsers"], organizations.organisations_fetchUsers, name="organisations_fetchUsers"),
    path(paths["organisations_createRole"], organizations.organisations_createRole, name="organisations_createRole"),
    path(paths["organisations_deleteUser"], organizations.organisations_deleteUser, name="organisations_deleteUser"),
    path(paths["organisations_getInviteLink"], organizations.organisations_getInviteLink, name="organisations_getInviteLink"),
    path(paths["organisations_assignRole"], organizations.organisations_assignRole, name="organisations_assignRole"),
    path(paths["organisations_getRoles"], organizations.organisations_getRoles, name="organisations_getRoles"),
    path(paths["organisations_setPermissionsForRole"], organizations.organisations_setPermissionsForRole, name="organisations_setPermissionsForRole"),
    path(paths["organisations_getPermissions"], organizations.organisations_getPermissions, name="organisations_getPermissions"),
    path(paths["organisations_getPermissionsForRole"], organizations.organisations_getPermissionsForRole, name="organisations_getPermissionsForRole"),
    path(paths["organisations_removeRole"], organizations.organisations_removeRole, name="organisations_removeRole"),
    path(paths["organisations_editRole"], organizations.organisations_editRole, name="organisations_editRole"),
    path(paths["organisations_deleteRole"], organizations.organisations_deleteRole, name="organisations_deleteRole"),
    path(paths["updateDetailsOfOrga"], profiles.updateDetailsOfOrganisation, name="updateDetailsOfOrganisation"),

    path(paths["isMagazineUp"], test_response.isMagazineUp, name="isMagazineUp"),

    path(paths["onto_getMaterials"], ontology.onto_getMaterials, name="getMaterials"),
    path(paths["onto_getMaterial"], ontology.onto_getMaterial, name="getMaterial"),
    path(paths["onto_getPrinters"], ontology.onto_getPrinters, name="getPrinters"),
    path(paths["onto_getPrinter"], ontology.onto_getPrinter, name="onto_getPrinter"),
    path(paths["orga_addPrinter"], ontology.orga_addPrinter, name="orga_addPrinter"),
    path(paths["orga_addPrinterEdit"], ontology.orga_addPrinterEdit, name="orga_addPrinterEdit"),
    path(paths["orga_createPrinter"], ontology.orga_createPrinter, name="orga_createPrinter"),
    path(paths["orga_removePrinter"], ontology.orga_removePrinter, name="orga_removePrinter"),
    path(paths["orga_getPrinters"], ontology.orga_getPrinters, name="orga_getPrinters"),
    path(paths["orga_addMaterial"], ontology.orga_addMaterial, name="orga_addMaterial"),
    path(paths["orga_addMaterialEdit"], ontology.orga_addMaterialEdit, name="orga_addPrinterEdit"),
    path(paths["orga_createMaterial"], ontology.orga_createMaterial, name="orga_createMaterial"),
    path(paths["orga_removeMaterial"], ontology.orga_removeMaterial, name="orga_removeMaterial"),
    path(paths["orga_getMaterials"], ontology.orga_getMaterials, name="orga_getMaterials"),

    path(paths["testQuery"], sparqlQueries.sendTestQuery, name="testQuery"),
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