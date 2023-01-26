from django.test import TestCase, Client
from django.http import HttpRequest, HttpResponse
from django.test.client import RequestFactory
import json
from .urls import paths

# Create your tests here.

# import classes here
#from .models import Question

from .handlers.test_response import *
class TestTestcalls(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        return super().setUp()

    def test_testResponse(self):
        """
        some logic, test if result is as expected
        """
        mockRequest = self.factory.get('/')
        response = testResponse(mockRequest)
        self.assertIs(response["testHeader"] == "TESTHEADER", True)

    def test_testResponseCsrf(self):
        mockRequest = self.factory.get('/')
        response = testResponseCsrf(mockRequest)
        self.assertIs("csrftoken" in response.cookies, True)


class TestProfiles(TestCase):

    def test_addUser(self):
        mockSession = self.client.session
        mockSession["user"] = {"userinfo": {"sub": "", "nickname": "", "email": "", "type": ""}}
        mockSession["user"]["userinfo"]["sub"] = "auth0|testuser"
        mockSession["user"]["userinfo"]["nickname"] = "testuser"
        mockSession["user"]["userinfo"]["email"] = "testuser@test.de"
        mockSession["user"]["userinfo"]["type"] = "user"
        mockSession.save()
        self.client.get("/"+paths["addUser"])
        response = json.loads(self.client.get("/"+paths["getUser"]).content)
        self.assertIs(response["name"] == "testuser" and response["email"] == "testuser@test.de", True)
    
    def test_updateUser(self):
        mockSession = self.client.session
        mockSession["user"] = {"userinfo": {"sub": "", "nickname": "", "email": "", "type": ""}}
        mockSession["user"]["userinfo"]["sub"] = "auth0|testuser2"
        mockSession["user"]["userinfo"]["nickname"] = "testuser2"
        mockSession["user"]["userinfo"]["email"] = "testuser2@test.de"
        mockSession["user"]["userinfo"]["type"] = "user"
        mockSession.save()
        self.client.get("/"+paths["addUser"])
        mockSession["user"]["userinfo"]["email"] = "testuser2_updated@test.de"
        mockSession.save()
        self.client.get("/"+paths["updateUser"])
        response = json.loads(self.client.get("/"+paths["getUser"]).content)
        self.assertIs(response["name"] == "testuser2" and response["email"] == "testuser2_updated@test.de", True)
    
    def test_deleteUser(self):      
        mockSession = self.client.session
        mockSession["user"] = {"userinfo": {"sub": "", "nickname": "", "email": "", "type": ""}}
        mockSession["user"]["userinfo"]["sub"] = "auth0|testuser3"
        mockSession["user"]["userinfo"]["nickname"] = "testuser3"
        mockSession["user"]["userinfo"]["email"] = "testuser3@test.de"
        mockSession["user"]["userinfo"]["type"] = "user"
        mockSession.save()
        self.client.get("/"+paths["addUser"])
        response = json.loads(self.client.get("/"+paths["getUser"]).content)
        self.assertIs(response["name"] == "testuser3" and response["email"] == "testuser3@test.de", True)

        delResponse = self.client.delete("/"+paths["deleteUser"])
        self.assertIs(delResponse.status_code == 200, True)

