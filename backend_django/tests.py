"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Tests for various functions and services
"""


from django.test import TestCase, Client
from django.http import HttpRequest, HttpResponse
from django.test.client import RequestFactory
import datetime
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
        mockSession["usertype"] = "indefinite"
        mockSession["user"]["tokenExpiresOn"] = str(datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=1677589627))
        mockSession.save()
        self.client.get("/"+paths["addUser"])
        response = json.loads(self.client.get("/"+paths["getUser"]).content)
        self.assertIs(response["name"] == "testuser" and response["email"] == "testuser@test.de", True)
    
    def test_updateUserName(self):
        mockSession = self.client.session
        mockSession["user"] = {"userinfo": {"sub": "", "nickname": "", "email": "", "type": ""}}
        mockSession["user"]["userinfo"]["sub"] = "auth0|testuser2"
        mockSession["user"]["userinfo"]["nickname"] = "testuser2"
        mockSession["user"]["userinfo"]["email"] = "testuser2@test.de"
        mockSession["usertype"] = "indefinite"
        mockSession["user"]["tokenExpiresOn"] = str(datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=1677589627))
        mockSession.save()
        self.client.get("/"+paths["addUser"])
        self.client.get("/"+paths["updateName"],headers={"username": "testuser2TEST"})
        response = json.loads(self.client.get("/"+paths["getUser"]).content)
        self.assertIs(response["name"] == "testuser2TEST", True)
    
    def test_deleteUser(self):      
        mockSession = self.client.session
        mockSession["user"] = {"userinfo": {"sub": "", "nickname": "", "email": "", "type": ""}}
        mockSession["user"]["userinfo"]["sub"] = "auth0|testuser3"
        mockSession["user"]["userinfo"]["nickname"] = "testuser3"
        mockSession["user"]["userinfo"]["email"] = "testuser3@test.de"
        mockSession["usertype"] = "indefinite"
        mockSession["user"]["tokenExpiresOn"] = str(datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=1677589627))
        mockSession.save()
        self.client.get("/"+paths["addUser"])
        response = json.loads(self.client.get("/"+paths["getUser"]).content)
        self.assertIs(response["name"] == "testuser3" and response["email"] == "testuser3@test.de", True)

        delResponse = self.client.delete("/"+paths["deleteUser"])
        self.assertIs(delResponse.status_code == 200, True)

class TestRedis(TestCase):

    def testRedis(self):
        response = json.loads(self.client.get("/"+paths["testRedis"]).content)
        self.assertIs(response["result"] == ["testvalue", True], True)
    
    def testUploadFile(self):
        # create File in memory
        # call to uploadFileTemporary as POST with file in FILES
        # call testGetUploadedFiles and check if file is the same via md5
        pass

class TestOrders(TestCase):

    def testAddingToCart(self):
        # mock cart data structure 
        # create mock session
        # send to updateCart with mock in body as json
        # test with getCart if worked
        pass
    
    def testGetManufacturers(self):
        # create manufacturer in database
        # log in by creating a "user" token in session
        # call getManufacturers
        # check if created one is the same as the result
        pass

    def testCheckPrintability(self):
        # log in by creating a "user" token in session
        # create mock cart and save to session
        # call checkPrintability
        # If answer is "Printable", it worked
        pass

    def testCheckPrice(self):
        # log in by creating a "user" token in session
        # create mock cart and save to session
        # call checkPrice
        # If answer an integer, it worked
        pass

    def testCheckLogistics(self):
        # log in by creating a "user" token in session
        # create mock cart and save to session
        # call checkLogistics
        # If answer an integer, it worked
        pass

    def testSendOrder(self):
        # log in by creating a "user" token in session
        # create mock cart and save to session
        # call sendOrder
        # call to database to get Order
        # If Order is the same, it worked
        pass

class TestDashboard(TestCase):

    def testRetrieveOrders(self):
        # create manufacturer
        # log in by creating a "user" token in session
        # create cart and save to session and into database via sendOrder
        # call retrieveOrders
        # if order is the same, it worked
        pass
    
    def testUpdateOrder(self):
        # create manufacturer
        # log in by creating a "user" token in session
        # create cart and save to session and into database via sendOrder
        # call updateOrder with PUT and json body
        # call retrieveOrders
        # if order was changed, it worked
        pass

    def testDeleteOrder(self):
        # create manufacturer
        # log in by creating a "user" token in session
        # create cart and save to session and into database via sendOrder
        # call retrieveOrder to get ID
        # call deleteOrder with DELETE and body as json with id of order
        # call retrieveOrder
        # if empty, it worked
        pass

    def testDeleteOrder(self):
        # create manufacturer
        # log in by creating a "user" token in session
        # create cart and save to session and into database via sendOrder
        # call retrieveOrder to get orderCollectionID
        # call deleteOrder with DELETE and body as json with id of orderCollection
        # call retrieveOrder
        # if empty, it worked
        pass
    
    def testGetMissedEvents(self):
        # create manufacturer and save login data (time)
        # log in as user
        # create cart and save to session and into database via sendOrder
        # log in as manufacturer
        # call getMissedEvents
        # if json output is not empty, it worked
        pass

class TestFilters(TestCase):

    def TestGetFilters(self):
        # create filters in format of frontend
        # send via POST as body to getFilters
        # if json is as expected, it worked
        pass

    def TestGetPostProcessing(self):
        # create filters in format of frontend
        # send via POST as body to getPostProcessing
        # if json is as expected and contains postProcessing stuff, it worked
        pass

    def TestGetMaterials(self):
        # create filters in format of frontend
        # send via POST as body to getMaterials
        # if json is as expected and contains postProcessing stuff, it worked
        pass

    def TestGetModels(self):
        # create filters in format of frontend
        # send via POST as body to getModels
        # if json is as expected and contains postProcessing stuff, it worked
        pass