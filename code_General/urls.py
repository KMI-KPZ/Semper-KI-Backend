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
from django.conf.urls import handler404

##############################################################################
### WSGI

from .handlers import admin, authentification, email, files, frontpage, organizations, profiles, statistics, websocket, testResponse, files
from Benchy.BenchyMcMarkface import startFromDjango

paths = { 
    "landingPage": ("",frontpage.landingPage),
    "benchyPage": ("private/benchy/",frontpage.benchyPage),
    "benchyMcMarkface": ("private/benchyMcMarkface/",startFromDjango),

    "test": ('public/test/',testResponse.testResponse),
    "csrfTest": ('public/testCsrf/',testResponse.testResponseCsrf),
    "csrfCookie": ('public/csrfCookie/',testResponse.testResponseCsrf),
    "dynamicTest": ('public/dynamic/',testResponse.dynamic),

    "login" : ("public/login/",authentification.loginUser),
    "logout": ("public/logout/",authentification.logoutUser),
    "callback": ("public/callback/",authentification.callbackLogin),
    "isLoggedIn": ("public/isLoggedIn/",authentification.isLoggedIn),
    "getRoles": ("public/getRoles/",authentification.getRolesOfUser),
    "getPermissions": ("public/getPermissions/",authentification.getPermissionsOfUser),
    "getNewPermissions": ("public/getNewPermissions/",authentification.getNewRoleAndPermissionsForUser),
    "getPermissionsFile": ("public/getPermissionMask/",authentification.provideRightsFile),

    "deleteUser": ("public/profileDeleteUser/",profiles.deleteUser),
    "addUser": ("private/profile_addUser/",profiles.addUserTest),
    "addOrga": ("private/profile_addOrga/",profiles.addOrganizationTest),
    "getUser": ("public/getUser/",profiles.getUserDetails),
    "getOrganization": ("public/getOrganization/",profiles.getOrganizationDetails),
    "updateDetails": ("public/updateUserDetails/",profiles.updateDetails),
    "updateDetailsOfOrga": ("public/updateOrganizationDetails/",profiles.updateDetailsOfOrganization),
    "deleteOrganization": ("public/deleteOrganization/",profiles.deleteOrganization),

    "genericUploadFiles": ("private/genericUploadFiles/",files.genericUploadFiles),
    "genericDownloadFile": ("private/genericDownloadFile/",files.genericDownloadFile),
    "genericDownloadFilesAsZip": ("private/genericDownloadFilesAsZip/",files.genericDownloadFilesAsZip),
    "genericDeleteFile": ("private/genericDeleteFile/",files.genericDeleteFile),

    "adminGetAll": ("public/admin/getAll/",admin.getAllAsAdmin),
    "adminDelete": ("public/admin/deleteUser/",admin.deleteUserAsAdmin),
    "adminDeleteOrga": ("public/admin/deleteOrganization/",admin.deleteOrganizationAsAdmin),
    "adminUpdateUser": ("public/admin/updateUser/",admin.updateDetailsOfUserAsAdmin),
    "adminUpdateOrga": ("public/admin/updateOrganization/",admin.updateDetailsOfOrganizationAsAdmin),

    "organizations_addUser": ("public/organizations/addUser/",organizations.organizations_addUser),
    "organizations_getInviteLink": ("public/organizations/getInviteLink/",organizations.organizations_getInviteLink),
    "organizations_fetchUsers": ("public/organizations/fetchUsers/",organizations.organizations_fetchUsers),
    "organizations_deleteUser": ("public/organizations/deleteUser/",organizations.organizations_deleteUser),
    "organizations_createRole": ("public/organizations/createRole/",organizations.organizations_createRole),
    "organizations_getRoles": ("public/organizations/getRoles/",organizations.organizations_getRoles),
    "organizations_assignRole": ("public/organizations/assignRole/",organizations.organizations_assignRole),
    "organizations_removeRole": ("public/organizations/removeRole/",organizations.organizations_removeRole),
    "organizations_editRole": ("public/organizations/editRole/",organizations.organizations_editRole),
    "organizations_deleteRole": ("public/organizations/deleteRole/",organizations.organizations_deleteRole),
    "organizations_getPermissions": ("public/organizations/getPermissions/",organizations.organizations_getPermissions),
    "organizations_getPermissionsForRole": ("public/organizations/getPermissionsForRole/",organizations.organizations_getPermissionsForRole),
    "organizations_setPermissionsForRole": ("public/organizations/setPermissionsForRole/",organizations.organizations_setPermissionsForRole),
    "organizations_createOrganization": ("public/organizations/createNew/",organizations.organizations_createNewOrganization),

    "statistics": ("public/getStatistics/",statistics.getNumberOfUsers),

    "contactForm": ("public/contact/",email.send_contact_form),
}

urlpatterns = [
    re_path(r'^private/doc', frontpage.docPage, name="docPage"),
    
    path('private/test/', testResponse.testResponse, name='test_response'),
    path('private/testWebsocket/', testResponse.testCallToWebsocket, name='testCallToWebsocket'),
]

if settings.DEBUG:
    urlpatterns.append(path('private/settings', frontpage.getSettingsToken, name='getSettingsToken'))

# add paths
for entry in paths:
    key = entry
    pathTuple = paths[entry]
    pathItself = pathTuple[0]
    handler = pathTuple[1]
    urlpatterns.append(path(pathItself, handler, name=key))

# any illegitimate requests are given a fu and their ip will be logged. Works only if DEBUG=False
handler404 = statistics.getIpAdress

##############################################################################
### ASGI
from .handlers.websocket import GeneralWebSocket

websockets = [
    path("ws/generalWebsocket/", GeneralWebSocket.as_asgi(), name="Websocket")
]