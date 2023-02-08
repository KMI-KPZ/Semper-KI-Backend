"""backend_django URL Configuration

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

from .handlers import test_response, authentification, profiles, filter, frontpage, sparqlQueries, files


paths = {
    "landingPage": "",
    "test": 'public/test/',
    "csrfTest": 'public/testCsrf/',
    "csrfCookie": 'public/csrfCookie/',
    "login" : "public/login/",
    "logout": "public/logout/",
    "callback": "public/callback/",
    "getUser": "public/getUser/",
    "getData": 'public/getData/',
    "deleteUser": "public/profileDeleteUser/",
    "addUser": "private/profile_addUser/",
    "getUserTest": "private/profile_getUser/",
    "updateUser": "public/updateUser/",
    "testQuery": "private/testquery/",
    "isLoggedIn": "public/isLoggedIn/",
    "testRedis": "private/testRedis/"
}



urlpatterns = [
    path(paths["landingPage"], frontpage.landingPage, name="landingPage"),
    re_path(r'^public/doc', frontpage.docPage, name="docPage"),
    path(paths["test"], test_response.testResponse, name='test_response'),
    path(paths["csrfTest"], test_response.testResponseCsrf, name='test_response_csrf'),
    path(paths["csrfCookie"], test_response.testResponseCsrf, name='test_response_csrf'),
    path(paths["login"], authentification.loginUser, name="loginUser"),
    path(paths["logout"], authentification.logoutUser, name="logoutUser"),
    path(paths["callback"], authentification.callbackLogin, name="callbackLogin"),
    path(paths["getUser"], authentification.getAuthInformation, name="getAuthInformation"),
    path(paths["getData"], filter.getData, name='getData'),
    path(paths["deleteUser"], profiles.deleteUser, name="deleteUser"),
    #path("private/testDB/", profiles.checkConnection, name="checkConnection"),
    #path("private/createDB/", profiles.createTable, name="createTable"),
    #path("private/insertInDB/", profiles.insertUser, name="insertUser"),
    path('private/test/', test_response.testResponse, name='test_response'),
    path(paths["addUser"], profiles.addUser, name="addUser"),
    path(paths["getUserTest"], profiles.getUserTest, name="getUserTest"),
    path(paths["updateUser"], profiles.updateUser, name="updateUser"),
    path(paths["testQuery"], sparqlQueries.testQuery, name="testQuery"),
    path(paths["isLoggedIn"], authentification.isLoggedIn, name="isLoggedIn"),
    path(paths["testRedis"], files.testRedis, name="testRedis")
]
