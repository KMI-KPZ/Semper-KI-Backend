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
    path('testCsrf/', test_response.testResponseCsrf, name='test_response_csrf'),
    path('csrfCookie/', test_response.testResponseCsrf, name='test_response_csrf'),
    path("login", authentification.loginUser, name="loginUser"),
    path("logout", authentification.logoutUser, name="logoutUser"),
    path("callback", authentification.callbackLogin, name="callbackLogin"),
    path("getUser/", authentification.getAuthInformation, name="getAuthInformation"),
    path("testDB/", profiles.checkConnection, name="checkConnection"),
    path("createDB/", profiles.createTable, name="createTable"),
    path("insertInDB/", profiles.insertUser, name="insertUser"),
    path("addUser/", profiles.addUser, name="addUser")
]
