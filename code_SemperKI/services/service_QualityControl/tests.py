"""
Part of Semper-KI software

Silvio Weging 2023
Lukas Hein 2025

Contains: Tests for various functions and services
"""


from django.test import TestCase, Client
import datetime
import json, io
from .urls import paths

from Generic_Backend.code_General.definitions import SessionContent, UserDescription, OrganizationDescription, ProfileClasses, FileObjectContent
from code_SemperKI.definitions import ProjectDescription, ProcessDescription, SessionContentSemperKI, ProcessUpdates
from .definitions import ServiceDetails

# Create your tests here.

#######################################################
class TestQualityControl(TestCase):
    testFile = io.BytesIO(b'binary stl file                                                                \x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x80\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00')
    
    # not part of the tests!
    #######################################################
    @classmethod
    def createOrganization(self, client:Client, id="", userID = ""):
        mockSession = client.session
        mockSession[SessionContent.MOCKED_LOGIN] = True
        mockSession[SessionContent.IS_PART_OF_ORGANIZATION] = True
        mockSession[SessionContent.PG_PROFILE_CLASS] = "organization"
        mockSession[SessionContent.usertype] = "organization"
        mockSession[SessionContent.PATH_AFTER_LOGIN] = "127.0.0.1:3000" # no real use but needs to be set
        mockSession.save()
        client.get("/"+paths["callbackLogin"][0])
        client.patch("/"+paths["updateDetailsOfOrga"][0], data={"changes": { "supportedServices": [6] } }, content_type="application/json")
        return mockSession

    #######################################################
    @staticmethod
    def createUser(client:Client):
        mockSession = client.session
        mockSession[SessionContent.MOCKED_LOGIN] = True
        mockSession[SessionContent.IS_PART_OF_ORGANIZATION] = False
        mockSession[SessionContent.PG_PROFILE_CLASS] = "user"
        mockSession[SessionContent.usertype] = "user"
        mockSession[SessionContent.PATH_AFTER_LOGIN] = "127.0.0.1:3000" # no real use but needs to be set
        mockSession.save()
        client.get("/"+paths["callbackLogin"][0])
        return mockSession
    
    #######################################################
    @staticmethod
    def createProjectAndProcess(client:Client):
        projectObj = json.loads(client.post("/"+paths["createProjectID"][0], data= {"title": "my_title"}).content)
        processPathSplit = paths["createProcessID"][0].split("/")
        processPath = processPathSplit[0]+"/"+processPathSplit[1]+"/"+processPathSplit[2]+"/"+projectObj[ProjectDescription.projectID]+"/"
        processObj = json.loads(client.get("/"+processPath).content)
        return (projectObj, processObj)
    
    #######################################################
    @staticmethod
    def createKG(client:Client):
        # test graph for system
        client.get("/"+paths["loadTestGraph"][0])
        # one node for materials
        client.get("/"+paths["orga_cloneTestGraphToOrgaForTests"][0])
        return None

    #######################################################
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.orgaClient = Client()
        self.createOrganization(self.orgaClient)
        self.createKG(self.orgaClient)
        
    # Tests!
    ##################################################
    def test_getContractors(self):
        client = Client()

        # Create user, project and process
        self.createUser(client)
        projectObj, processObj = self.createProjectAndProcess(client)

        # TODO set stuff so that the service is complete

        # # set service type to 6
        # changes = {"projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { "serviceType": 6}, "deletions":{} }
        # response = client.patch("/"+paths["updateProcess"][0], data=json.dumps(changes), content_type="application/json")
        # self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        # getProcPathSplit = paths["getProcess"][0].split("/")
        # getProcPath = getProcPathSplit[0] + "/" + getProcPathSplit[1] + "/" + getProcPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] + "/" + processObj[ProcessDescription.processID] + "/"
        # response = json.loads(client.get("/"+getProcPath).content)
        # fileID = list(response[ProcessDescription.files].keys())[0]

        # # advance state to service finished
        # getProcPathSplit = paths["getProcess"][0].split("/")
        # getProcPath = getProcPathSplit[0] + "/" + getProcPathSplit[1] + "/" + getProcPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] + "/" + processObj[ProcessDescription.processID] + "/"
        # response = json.loads(client.get("/"+getProcPath).content)
        # self.assertIs("processStatusButtons" in response and len(response["processStatusButtons"]) > 0 and "action" in response["processStatusButtons"][2], True, f'{response}')
        # buttonData = response["processStatusButtons"][2]["action"]["data"]
        # button = {"buttonData":buttonData, "projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]]}
        # response = client.post("/"+paths["statusButtonRequest"][0], json.dumps(button), content_type="application/json")
        # self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        # # call getContractors as get with processID in path
        # contractorsPath = paths["getContractors"][0].split("/")
        # contractorsPath = contractorsPath[0] + "/" + contractorsPath[1] + "/" + contractorsPath[2] + "/" + contractorsPath[3] + "/" + processObj[ProcessDescription.processID] + "/"
        # response = client.get("/"+contractorsPath)
        # self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        # response = json.loads(client.get("/"+contractorsPath).content)
        # # Check return value for length of contractors
        # self.assertIs(len(response)>=1, True, f'{len(response)} < 1')
