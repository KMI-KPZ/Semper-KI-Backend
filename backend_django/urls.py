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

from .handlers import test_response, authentification, profiles, filter, frontpage, sparqlQueries, files, statistics, checkOrder, dashboard, organizations, ontology, orderManagement
from Benchy.BenchyMcMarkface import startFromDjango
from django.conf.urls.static import static

paths = {
    "landingPage": "",
    "benchyPage": "private/benchy/",
    "benchyMcMarkface": "private/benchyMcMarkface/",

    "test": 'public/test/',
    "csrfTest": 'public/testCsrf/',
    "csrfCookie": 'public/csrfCookie/',

    "login" : "public/login/",
    "logout": "public/logout/",
    "callback": "public/callback/",
    "isLoggedIn": "public/isLoggedIn/",
    "getRoles": "public/getRoles/",
    "getPermissions": "public/getPermissions/",
    "getNewPermissions": "public/getNewPermissions/",
    "getPermissionsFile": "public/getPermissionMask/",
    "updateRole": "public/updateRole/",
    
    "getProcessData": 'public/getProcessData/',
    "getModels": 'public/getModels/',
    "getFilters": 'public/getFilters/',
    "getMaterials": 'public/getMaterials/',
    "getPostProcessing": 'public/getPostProcessing/',

    "updateCart": "public/updateCart/",
    "getCart": "public/getCart/",
    "getManufacturers": "public/getManufacturers/",
    "checkPrintability": "public/checkPrintability/",
    "checkPrices": "public/checkPrices/",
    "checkLogistics": "public/checkLogistics/",
    "sendOrder": "public/sendOrder/",

    "retrieveOrders": "public/getOrders/",
    "getMissedEvents": "public/getMissedEvents/",

    "getFlatOrders": "public/getFlatOrders/",
    "createOrder": "public/createOrder/",
    "getOrder": "public/getOrder/<orderCollectionID>/",
    "createSubOrder": "public/createSubOrder/<orderCollectionID>/",
    "updateOrder": "public/updateSubOrder/",
    "updateOrderCollection": "public/updateOrder/",
    "deleteOrder": "public/deleteSubOrder/<orderCollectionID>/<orderID>/",
    "deleteOrderCollection": "public/deleteOrder/<orderCollectionID>/",


    "deleteUser": "public/profileDeleteUser/",
    "addUser": "private/profile_addUser/",
    "getUserTest": "private/profile_getUser/",
    "getUser": "public/getUser/",
    "getOrganization": "public/getOrganization/",
    "updateDetails": "public/updateUserDetails/",
    "updateDetailsOfOrga": "public/updateOrganizationDetails/",
    "deleteOrganization": "public/deleteOrganization/",
    
    "adminGetAll": "public/admin/getAll/",
    "adminDelete": "public/admin/deleteUser/",
    "adminDeleteOrga": "public/admin/deleteOrganization/",

    "organizations_addUser": "public/organizations/addUser/",
    "organizations_getInviteLink": "public/organizations/getInviteLink/",
    "organizations_fetchUsers": "public/organizations/fetchUsers/",
    "organizations_deleteUser": "public/organizations/deleteUser/",
    "organizations_createRole": "public/organizations/createRole/",
    "organizations_getRoles": "public/organizations/getRoles/",
    "organizations_assignRole": "public/organizations/assignRole/",
    "organizations_removeRole": "public/organizations/removeRole/",
    "organizations_editRole": "public/organizations/editRole/",
    "organizations_deleteRole": "public/organizations/deleteRole/",
    "organizations_getPermissions": "public/organizations/getPermissions/",
    "organizations_getPermissionsForRole": "public/organizations/getPermissionsForRole/",
    "organizations_setPermissionsForRole": "public/organizations/setPermissionsForRole/",
    "organizations_createOrganization": "public/organizations/createNew/",

    "isMagazineUp": "public/isMagazineUp/",

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

    "testQuery": "private/testquery/",
    "sendQuery": "private/sendQuery/",
    "testQuerySize": "private/query/",

    "testRedis": "private/testRedis/",
    "uploadModels": "public/uploadModels/", #uploadModels uploadFiles
    "retrieveFilesTEST": "private/retrieveFiles/",
    "getFileFromOrder": "public/getFileFromOrder/",

    "statistics": "public/getStatistics/",
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

    #path(paths["updateCart"], checkOrder.updateCart, name='updateCart'),
    #path(paths["getCart"], checkOrder.getCart, name='getCart'),
    path(paths["getManufacturers"], checkOrder.getManufacturers, name='getManufacturers'),
    path(paths["checkPrintability"], checkOrder.checkPrintability, name='checkPrintability'),
    path(paths["checkPrices"], checkOrder.checkPrice, name='checkPrice'),
    path(paths["checkLogistics"], checkOrder.checkLogistics, name='checkLogistics'),

    path(paths["retrieveOrders"], dashboard.retrieveOrders, name='retrieveOrders'),
    #path(paths["updateOrder"], dashboard.updateOrder, name='updateOrder'),
    path(paths["getMissedEvents"], dashboard.getMissedEvents, name='getMissedEvents'),

    path(paths["getFlatOrders"], orderManagement.getFlatOrders, name="getFlatOrders"),
    path(paths["createOrder"], orderManagement.createOrderCollectionID, name="createOrderCollectionID"),
    path(paths["createSubOrder"], orderManagement.createOrderID, name="createOrderID"),
    path(paths["getOrder"], orderManagement.getOrder, name="getOrder"),
    path(paths["sendOrder"], orderManagement.sendOrder, name='sendOrder'),
    path(paths["updateOrder"], orderManagement.updateOrder, name='updateOrder'),
    path(paths["updateOrderCollection"], orderManagement.updateOrderCollection, name='updateOrderCollection'),
    path(paths["deleteOrder"], orderManagement.deleteOrder, name='deleteOrder'),
    path(paths["deleteOrderCollection"], orderManagement.deleteOrderCollection, name='deleteOrderCollection'),


    path(paths["deleteUser"], profiles.deleteUser, name="deleteUser"),
    #path("private/testDB/", profiles.checkConnection, name="checkConnection"),
    #path("private/createDB/", profiles.createTable, name="createTable"),
    #path("private/insertInDB/", profiles.insertUser, name="insertUser"),
    #path(paths["addUser"], profiles.addUserTest, name="addUser"),
    #path(paths["getUserTest"], profiles.getUserTest, name="getUserTest"),
    path(paths["updateDetails"], profiles.updateDetails, name="updateDetails"),
    #path(paths["updateRole"], profiles.updateRole, name="updateRole"),
    path(paths["getUser"], profiles.getUserDetails, name="getUserDetails"),
    path(paths["getOrganization"], profiles.getOrganizationDetails, name="getOrganizationDetails"),
    path(paths["updateDetailsOfOrga"], profiles.updateDetailsOfOrganization, name="updateDetailsOfOrganization"),
    path(paths["deleteOrganization"], profiles.deleteOrganization, name="deleteOrganization"),

    path(paths["adminGetAll"], profiles.getAll, name="getAll"),
    path(paths["adminDelete"], profiles.deleteUserAsAdmin, name="deleteUserAsAdmin"),
    path(paths["adminDeleteOrga"], profiles.deleteOrganizationAsAdmin, name="deleteOrganizationAsAdmin"),

    path(paths["organizations_addUser"], organizations.organizations_addUser, name="organizations_addUser"),
    path(paths["organizations_fetchUsers"], organizations.organizations_fetchUsers, name="organizations_fetchUsers"),
    path(paths["organizations_createRole"], organizations.organizations_createRole, name="organizations_createRole"),
    path(paths["organizations_deleteUser"], organizations.organizations_deleteUser, name="organizations_deleteUser"),
    path(paths["organizations_getInviteLink"], organizations.organizations_getInviteLink, name="organizations_getInviteLink"),
    path(paths["organizations_assignRole"], organizations.organizations_assignRole, name="organizations_assignRole"),
    path(paths["organizations_getRoles"], organizations.organizations_getRoles, name="organizations_getRoles"),
    path(paths["organizations_setPermissionsForRole"], organizations.organizations_setPermissionsForRole, name="organizations_setPermissionsForRole"),
    path(paths["organizations_getPermissions"], organizations.organizations_getPermissions, name="organizations_getPermissions"),
    path(paths["organizations_getPermissionsForRole"], organizations.organizations_getPermissionsForRole, name="organizations_getPermissionsForRole"),
    path(paths["organizations_removeRole"], organizations.organizations_removeRole, name="organizations_removeRole"),
    path(paths["organizations_editRole"], organizations.organizations_editRole, name="organizations_editRole"),
    path(paths["organizations_deleteRole"], organizations.organizations_deleteRole, name="organizations_deleteRole"),
    path(paths["organizations_createOrganization"], organizations.organizations_createNewOrganization, name="organizations_createNewOrganization"),

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

if settings.DEBUG:
    urlpatterns.append(path('private/settings', frontpage.getSettingsToken, name='getSettingsToken'))

urlpatterns.append(re_path(r'^.*', statistics.getIpAdress, name="everythingElse"))

##############################################################################
### ASGI
from .handlers.test_response import testWebSocket
from .handlers.websocket import GeneralWebSocket

websockets = [
    #path("ws/testWebsocket/", testWebSocket.as_asgi(), name="testAsync"),
    path("ws/generalWebsocket/", GeneralWebSocket.as_asgi(), name="Websocket")
]