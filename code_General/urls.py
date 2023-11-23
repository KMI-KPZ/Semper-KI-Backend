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

from django.urls import path, re_path
from django.conf import settings

##############################################################################
### WSGI

from .handlers import admin, authentification, email, files, frontpage, organizations, profiles, statistics, websocket, testResponse
from Benchy.BenchyMcMarkface import startFromDjango

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
    "adminUpdateUser": "public/admin/updateUser/",
    "adminUpdateOrga": "public/admin/updateOrganization/",

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

    "statistics": "public/getStatistics/",

    "contactForm": "public/contact/",
}

urlpatterns = [
    path(paths["landingPage"], frontpage.landingPage, name="landingPage"),
    path(paths["benchyPage"], frontpage.benchyPage, name="benchy"),
    path(paths["benchyMcMarkface"], startFromDjango, name="benchyMcMarkface"),

    re_path(r'^public/doc', frontpage.docPage, name="docPage"),
    
    path(paths["test"], testResponse.testResponse, name='test_response'),
    path(paths["csrfTest"], testResponse.testResponseCsrf, name='test_response_csrf'),
    path(paths["csrfCookie"], testResponse.testResponseCsrf, name='test_response_csrf'),
    path('private/test/', testResponse.testResponse, name='test_response'),
    path('private/testWebsocket/', testResponse.testCallToWebsocket, name='testCallToWebsocket'),

    path(paths["login"], authentification.loginUser, name="loginUser"),
    path(paths["logout"], authentification.logoutUser, name="logoutUser"),
    path(paths["callback"], authentification.callbackLogin, name="callbackLogin"),
    path(paths["isLoggedIn"], authentification.isLoggedIn, name="isLoggedIn"),
    path(paths["getRoles"], authentification.getRolesOfUser, name="getRoles"),
    path(paths["getPermissions"], authentification.getPermissionsOfUser, name="getPermissions"),
    path(paths["getNewPermissions"], authentification.getNewRoleAndPermissionsForUser, name="getNewPermissions"),
    path(paths["getPermissionsFile"], authentification.provideRightsFile, name="getPermissionsFile"),

    path(paths["deleteUser"], profiles.deleteUser, name="deleteUser"),
    #path(paths["addUser"], profiles.addUserTest, name="addUser"),
    #path(paths["getUserTest"], profiles.getUserTest, name="getUserTest"),
    path(paths["updateDetails"], profiles.updateDetails, name="updateDetails"),
    path(paths["getUser"], profiles.getUserDetails, name="getUserDetails"),
    path(paths["getOrganization"], profiles.getOrganizationDetails, name="getOrganizationDetails"),
    path(paths["updateDetailsOfOrga"], profiles.updateDetailsOfOrganization, name="updateDetailsOfOrganization"),
    path(paths["deleteOrganization"], profiles.deleteOrganization, name="deleteOrganization"),

    path(paths["adminGetAll"], admin.getAllAsAdmin, name="getAllAsAdmin"),
    path(paths["adminDelete"], admin.deleteUserAsAdmin, name="deleteUserAsAdmin"),
    path(paths["adminDeleteOrga"], admin.deleteOrganizationAsAdmin, name="deleteOrganizationAsAdmin"),
    path(paths["adminUpdateUser"], admin.updateDetailsOfUserAsAdmin, name="updateDetailsOfUserAsAdmin"),
    path(paths["adminUpdateOrga"], admin.updateDetailsOfOrganizationAsAdmin, name="updateDetailsOfOrganizationAsAdmin"),

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

    path(paths["contactForm"], email.send_contact_form, name="sendContactForm"),

    path(paths["statistics"], statistics.getNumberOfUsers, name="statistics")
]

if settings.DEBUG:
    urlpatterns.append(path('private/settings', frontpage.getSettingsToken, name='getSettingsToken'))

urlpatterns.append(re_path(r'^.*', statistics.getIpAdress, name="everythingElse"))

##############################################################################
### ASGI
from .handlers.websocket import GeneralWebSocket

websockets = [
    path("ws/generalWebsocket/", GeneralWebSocket.as_asgi(), name="Websocket")
]