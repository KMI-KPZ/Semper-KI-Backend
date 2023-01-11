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
from django.urls import include, path

from .handlers import test_response, authentification, profiles

urlpatterns = [
    path("", authentification.index, name="index"),
    path('test/', test_response.testResponse, name='test_response'),
    path('public/test/', test_response.testResponse, name='test_response'),
    path('private/test/', test_response.testResponse, name='test_response'),
    path('public/testCsrf/', test_response.testResponseCsrf, name='test_response_csrf'),
    path('public/csrfCookie/', test_response.testResponseCsrf, name='test_response_csrf'),
    path("public/login/", authentification.loginUser, name="loginUser"),
    path("public/logout/", authentification.logoutUser, name="logoutUser"),
    path("public/callback/", authentification.callbackLogin, name="callbackLogin"),
    path("private/getUser/", authentification.getAuthInformation, name="getAuthInformation"),
    #path("private/testDB/", profiles.checkConnection, name="checkConnection"),
    #path("private/createDB/", profiles.createTable, name="createTable"),
    #path("private/insertInDB/", profiles.insertUser, name="insertUser"),
    path("private/profile_addUser/", profiles.addUser, name="addUser"),
    path("private/profile_getUser/", profiles.getUser, name="getUser"),
    path("private/profile_updateUser/", profiles.updateUser, name="updateUser"),
    path("private/profile_deleteUser/", profiles.deleteUser, name="deleteUser")
]
