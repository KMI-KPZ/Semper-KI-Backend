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

from .handlers import test_response, authentification

urlpatterns = [
    path("", authentification.index, name="index"),
    path('test/', test_response.testResponse, name='test_response'),
    path('testCsrf/', test_response.testResponseCsrf, name='test_response_csrf'),
    path('csrfCookie/', test_response.testResponseCsrf, name='test_response_csrf'),
    path("login", authentification.login, name="login"),
    path("logout", authentification.logout, name="logout"),
    path("callback", authentification.callback, name="callback"),
    path("getUser/", authentification.getAuthInformation, name="getAuthInformation"),
    path("deleteSession/", authentification.deleteSessionCookie, name="deleteSessionCookie"),
    path('admin/', admin.site.urls),
]
