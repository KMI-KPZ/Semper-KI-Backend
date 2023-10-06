"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Tests for various functions and services
"""


from django.test import TestCase, Client
from django.http import HttpRequest, HttpResponse
from django.test.client import RequestFactory
import datetime
import json, io
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
        currentTime = datetime.datetime.now()
        mockSession["user"]["tokenExpiresOn"] = str(datetime.datetime(currentTime.year+1, currentTime.month, currentTime.day, currentTime.hour, currentTime.minute, currentTime.second, tzinfo=datetime.timezone.utc))
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
        currentTime = datetime.datetime.now()
        mockSession["user"]["tokenExpiresOn"] = str(datetime.datetime(currentTime.year+1, currentTime.month, currentTime.day, currentTime.hour, currentTime.minute, currentTime.second, tzinfo=datetime.timezone.utc))
        mockSession.save()
        self.client.get("/"+paths["addUser"])
        self.client.put("/"+paths["updateName"], '{"username": "testuser2TEST"}')
        response = json.loads(self.client.get("/"+paths["getUser"]).content)
        self.assertIs(response["name"] == "testuser2TEST", True)
    
    def test_deleteUser(self):      
        mockSession = self.client.session
        mockSession["user"] = {"userinfo": {"sub": "", "nickname": "", "email": "", "type": ""}}
        mockSession["user"]["userinfo"]["sub"] = "auth0|testuser3"
        mockSession["user"]["userinfo"]["nickname"] = "testuser3"
        mockSession["user"]["userinfo"]["email"] = "testuser3@test.de"
        mockSession["usertype"] = "indefinite"
        currentTime = datetime.datetime.now()
        mockSession["user"]["tokenExpiresOn"] = str(datetime.datetime(currentTime.year+1, currentTime.month, currentTime.day, currentTime.hour, currentTime.minute, currentTime.second, tzinfo=datetime.timezone.utc))
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

class TestProjects(TestCase):
    testFile = io.BytesIO(b'binary stl file                                                                \x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x80\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00')
    mockCart = {"cart": [{"title": "Cube_3d_printing_sample.stl", "model": {"id": "ceec76ddd0b621bb6d488aa5d6087320", "title": "Cube_3d_printing_sample.stl", "tags": [], "date": "2023-5-10", "license": "", "certificate": [], "URI": "", "createdBy": "user"}, "material": {"id": "a9ae8dcc04ef529de1153d5731c4d65c", "title": "PLA", "propList": ["Rigid", "Brittle", "Biodegradable"], "URI": "http://127.0.0.1:8000/public/static/public/media/testpicture.jpg"}, "postProcessings": [{"id": "d3c3ac57e13df2834f84f1f3d96546bf", "title": "postProcessing 0", "checked": True, "selectedValue": "", "valueList": ["selection2", "selection1"], "type": "selection", "URI": "http://127.0.0.1:8000/public/static/public/media/testpicture.jpg"}], "manufacturerID": "44f92f0d8186a77c2f88b7deb4a49004957734e5fd1c7ddab1932318d6d7f6eeb39c7b6f1b3e84035422d219bd3abdad665d07acb26a115a78dd34d612173407"}]}
    # not part of the tests!
    @classmethod
    def createManufacturer(self):
        mockSession = self.client.session
        mockSession["user"] = {"userinfo": {"sub": "", "nickname": "", "email": "", "type": ""}}
        mockSession["user"]["userinfo"]["sub"] = "auth0|testmanufacturer"
        mockSession["user"]["userinfo"]["nickname"] = "testmanufacturer"
        mockSession["user"]["userinfo"]["email"] = "testmanufacturer@test.de"
        mockSession["user"]["userinfo"]["org_id"] = "id123"
        mockSession["userPermissions"] = [{"permission_name": "processes:read"},{"permission_name": "processes:files"},{"permission_name": "processes:chat"},{"permission_name": "processes:edit"},{"permission_name": "orga:edit"},{"permission_name": "orga:read"},{"permission_name": "resources:read"},{"permission_name": "resources:edit"}]
        mockSession["usertype"] = "organization"
        mockSession["organizationName"] = "manufacturer"
        currentTime = datetime.datetime.now()
        mockSession["user"]["tokenExpiresOn"] = str(datetime.datetime(currentTime.year+1, currentTime.month, currentTime.day, currentTime.hour, currentTime.minute, currentTime.second, tzinfo=datetime.timezone.utc))
        mockSession.save()
        self.client.get("/"+paths["addUser"])
        returnedJson = self.client.get("/"+paths["getManufacturers"])
        print(returnedJson)
        returnedJsonAsDict = json.loads(returnedJson.content)
        localMockCart = self.mockCart
        localMockCart["cart"][0]["manufacturerID"] = returnedJsonAsDict[0]["id"]
        self.mockCart = localMockCart

    @staticmethod
    def createUserInSession(mockSession):
        mockSession["user"] = {"userinfo": {"sub": "", "nickname": "", "email": "", "type": ""}}
        mockSession["user"]["userinfo"]["sub"] = "auth0|testuser"
        mockSession["user"]["userinfo"]["nickname"] = "testuser"
        mockSession["user"]["userinfo"]["email"] = "testuser@test.de"
        mockSession["userPermissions"] = [{"permission_name": "processes:read"},{"permission_name": "processes:files"},{"permission_name": "processes:chat"},{"permission_name": "processes:edit"},{"permission_name": "orga:edit"},{"permission_name": "orga:read"},{"permission_name": "resources:read"},{"permission_name": "resources:edit"}]
        mockSession["usertype"] = "user"
        currentTime = datetime.datetime.now()
        mockSession["user"]["tokenExpiresOn"] = str(datetime.datetime(currentTime.year+1, currentTime.month, currentTime.day, currentTime.hour, currentTime.minute, currentTime.second, tzinfo=datetime.timezone.utc))
        return mockSession

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.client = Client()
        self.createManufacturer()
    
    def testUploadModel(self):
        # call to uploadFileTemporary as POST with file in FILES
        mockSession = self.client.session
        returnedJson = self.client.post("/"+paths["uploadModels"], {'testfile.stl':self.testFile} )
        returnedJsonAsDict = json.loads(returnedJson.content)
        self.assertIs(len(returnedJsonAsDict["models"]) == 1, True)
    
    def testDownloadModel(self):
        # upload model to redis
        #mockSession = self.client.session
        #self.client.post("/"+paths["uploadModels"], {'testfile.stl':self.testFile} )
        # send post to downloadFiles

        # if md5 of upload and download equal, it worked
        pass

    def testAddingToCart(self):
        # mock cart data structure 
        # create mock session
        mockSession = self.client.session
        mockSession = self.createUserInSession(mockSession)
        mockSession.save()
        # send to updateCart with mock in body as json
        self.client.post("/"+paths["updateCart"], content_type="application/json", data=self.mockCart)
        # test with getCart if worked
        returnedJson = self.client.get("/"+paths["getCart"])
        returnedJsonAsDict = json.loads(returnedJson.content)
        self.assertIs(returnedJsonAsDict == self.mockCart, True)
    
    def testGetManufacturers(self):
        # create manufacturer in database
        # log in by creating a "user" token in session
        mockSession = self.client.session
        mockSession = self.createUserInSession(mockSession)
        mockSession.save()
        # call getManufacturers
        returnedJson = self.client.get("/"+paths["getManufacturers"])
        # check if created one is the same as the result
        returnedJsonAsDict = json.loads(returnedJson.content)
        self.assertIs(len(returnedJsonAsDict) >= 1, True)

    def testCheckPrintability(self):
        # log in by creating a "user" token in session
        mockSession = self.client.session
        mockSession = self.createUserInSession(mockSession)
        mockSession.save()
        # create mock cart and save to session
        self.client.post("/"+paths["updateCart"], content_type="application/json", data=self.mockCart)
        # call checkPrintability
        returnMessage = self.client.get("/"+ paths["checkPrintability"]).content
        # If answer is "Printable", it worked
        self.assertIs(returnMessage == b"Printable", True)

    def testCheckPrice(self):
        # log in by creating a "user" token in session
        mockSession = self.client.session
        mockSession = self.createUserInSession(mockSession)
        mockSession.save()
        # create mock cart and save to session
        self.client.post("/"+paths["updateCart"], content_type="application/json", data=self.mockCart)
        # call checkPrice
        returnMessage = self.client.get("/"+ paths["checkPrices"]).content.decode("UTF-8")
        # If answer an integer, it worked
        self.assertIs(int(returnMessage) > 0, True)

    def testCheckLogistics(self):
        # log in by creating a "user" token in session
        mockSession = self.client.session
        mockSession = self.createUserInSession(mockSession)
        mockSession.save()
        # create mock cart and save to session
        self.client.post("/"+paths["updateCart"], content_type="application/json", data=self.mockCart)
        # call checkLogistics
        returnMessage = self.client.get("/"+ paths["checkLogistics"]).content.decode("UTF-8")
        # If answer an integer, it worked
        self.assertIs(int(returnMessage) > 0, True)

    def testSendProcess(self):
        # log in by creating a "user" token in session
        mockSession = self.client.session
        mockSession = self.createUserInSession(mockSession)
        mockSession.save()
        testRet = self.client.get("/"+paths["addUser"])
        self.assertIs(testRet.content == b"Worked", True)

        # create mock cart and save to session
        self.client.post("/"+paths["updateCart"], content_type="application/json", data=self.mockCart)
        # call sendProcess
        testRet = self.client.get("/"+paths["sendProcess"])
        self.assertIs(testRet.content == b"Success", True)
        # call to database to get processes
        returnedJson = self.client.get("/"+paths["retrieveProcesses"])
        # If Process is the same, it worked
        returnedJsonAsDict = json.loads(returnedJson.content)
        self.assertIs(returnedJsonAsDict[0]["service"][0]["item"]["model"]["id"] == self.mockCart["cart"][0]["model"]["id"], True)

    #def testRetrieveOrders(self): redundant to testSendOrder

    #def testUpdateOrder(self): # redundant to testSendOrder

    def testDeleteOrder(self):
        # create manufacturer
        # log in by creating a "user" token in session
        mockSession = self.client.session
        mockSession = self.createUserInSession(mockSession)
        mockSession.save()
        testRet = self.client.get("/"+paths["addUser"])
        self.assertIs(testRet.content == b"Worked", True)
        # create cart and save to session and into database via sendOrder
        self.client.post("/"+paths["updateCart"], content_type="application/json", data=self.mockCart)
        # call sendOrder
        testRet = self.client.get("/"+paths["sendOrder"])
        # call retrieveOrder to get ID
        returnedJson = self.client.get("/"+paths["retrieveOrders"])
        returnedJsonAsDict = json.loads(returnedJson.content)
        orderID = returnedJsonAsDict[0]["orders"][0]["id"]
        # call deleteOrder with DELETE and body as json with id of order
        self.client.delete("/"+paths["deleteOrder"], content_type="application/json", data={"id": orderID})
        # call retrieveOrder
        returnedJson = self.client.get("/"+paths["retrieveOrders"])
        returnedJsonAsDict = json.loads(returnedJson.content)
        # if empty, it worked
        self.assertIs(len(returnedJsonAsDict) == 0, True)

    def testDeleteOrderCollection(self):
        # create manufacturer
        # log in by creating a "user" token in session
        mockSession = self.client.session
        mockSession = self.createUserInSession(mockSession)
        mockSession.save()
        testRet = self.client.get("/"+paths["addUser"])
        self.assertIs(testRet.content == b"Worked", True)
        # create cart and save to session and into database via sendOrder
        self.client.post("/"+paths["updateCart"], content_type="application/json", data=self.mockCart)
        # call sendOrder
        testRet = self.client.get("/"+paths["sendOrder"])
        # call retrieveOrder to get ID
        returnedJson = self.client.get("/"+paths["retrieveOrders"])
        returnedJsonAsDict = json.loads(returnedJson.content)
        orderCollectionID = returnedJsonAsDict[0]["id"]
        # call deleteOrderCollection with DELETE and body as json with id of orderCollection
        self.client.delete("/"+paths["deleteOrderCollection"], content_type="application/json", data={"id": orderCollectionID})
        # call retrieveOrder
        returnedJson = self.client.get("/"+paths["retrieveOrders"])
        returnedJsonAsDict = json.loads(returnedJson.content)
        # if empty, it worked
        self.assertIs(len(returnedJsonAsDict) == 0, True)
    
    def testGetMissedEvents(self):
        # create manufacturer and save login data (time)
        # log in as user
        # create cart and save to session and into database via sendOrder
        # updateOrder with Message
        # log in as manufacturer
        # call getMissedEvents
        # if json output is not empty, it worked
        pass

class TestFilters(TestCase):
    filters = {"filters": [{"id": 0, "isChecked": False, "isOpen": False, "question": {"isSelectable": True, "title": "costs", "category": "general", "type": "slider", "range": [0, 9999], "values": "null", "units": "\u20ac"}, "answer": "null"}]}

    def testGetFilters(self):
        # send via POST as body to getFilters
        returnedJson = self.client.post("/"+paths["getFilters"], content_type="application/json", data=self.filters)
        # if json is as expected, it worked
        returnedJsonAsDict = json.loads(returnedJson.content)
        self.assertIs(len(returnedJsonAsDict["filters"]) == 1, True) #TODO

    def testGetPostProcessing(self):
        # send via POST as body to getPostProcessing
        returnedJson = self.client.post("/"+paths["getPostProcessing"], content_type="application/json", data=self.filters)
        # if json is as expected and contains postProcessing stuff, it worked
        returnedJsonAsDict = json.loads(returnedJson.content)
        self.assertIs(len(returnedJsonAsDict["postProcessing"]) >= 1, True)
        pass

    def testGetMaterials(self):
        # send via POST as body to getMaterials
        returnedJson = self.client.post("/"+paths["getMaterials"], content_type="application/json", data=self.filters)
        # if json is as expected and contains materials stuff, it worked
        returnedJsonAsDict = json.loads(returnedJson.content)
        self.assertIs(len(returnedJsonAsDict["materials"]) >= 1, True)
        pass

    def testGetModels(self):
        # send via POST as body to getModels
        returnedJson = self.client.post("/"+paths["getModels"], content_type="application/json", data=self.filters)
        # if json is as expected and contains models stuff, it worked
        returnedJsonAsDict = json.loads(returnedJson.content)
        self.assertIs(len(returnedJsonAsDict["models"]) >= 1, True)
        pass