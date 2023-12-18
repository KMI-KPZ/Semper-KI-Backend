"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Tests for various functions and services
"""


from django.test import TestCase, Client
import datetime
import json, io
from .urls import paths

from code_General.definitions import SessionContent, UserDescription, OrganizationDescription, ProfileClasses, FileObjectContent
from code_SemperKI.definitions import ProjectDescription, ProcessDescription, SessionContentSemperKI, ProcessUpdates
from .definitions import ServiceDetails

# Create your tests here.

#######################################################
class TestAdditiveManufacturing(TestCase):
    testFile = io.BytesIO(b'binary stl file                                                                \x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x80\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00')
    
    # not part of the tests!
    #######################################################
    @classmethod
    def createOrganization(self, client:Client, id="", userID = ""):
        mockSession = client.session
        mockSession["user"] = {"userinfo": {"sub": "", "nickname": "", "email": "", "org_id": ""}}
        mockSession["user"]["userinfo"]["sub"] = "auth0|testOrga" if userID == "" else userID
        mockSession["user"]["userinfo"]["nickname"] = "testOrga"
        mockSession["user"]["userinfo"]["email"] = "testOrga@test.de"
        mockSession["user"]["userinfo"]["org_id"] = "id123" if id == "" else id
        mockSession[SessionContent.USER_PERMISSIONS] = {"processes:read": "", "processes:files": "", "processes:messages": "", "processes:edit" : "", "processes:delete": "", "orga:edit": "", "orga:delete": "", "orga:read": "", "resources:read": "", "resources:edit": ""}
        mockSession[SessionContent.usertype] = "organization"
        mockSession[SessionContent.ORGANIZATION_NAME] = "testOrga"
        mockSession[SessionContent.INITIALIZED] = True
        mockSession[SessionContent.PG_PROFILE_CLASS] = ProfileClasses.organization
        currentTime = datetime.datetime.now()
        mockSession["user"]["tokenExpiresOn"] = str(datetime.datetime(currentTime.year+1, currentTime.month, currentTime.day, currentTime.hour, currentTime.minute, currentTime.second, tzinfo=datetime.timezone.utc))
        mockSession.save()
        client.post("/"+paths["addOrga"][0])
        client.post("/"+paths["addUser"][0])
        client.patch("/"+paths["updateDetailsOfOrga"][0], '{"data": {"content": { "supportedServices": [1] } } }')
        return mockSession

    #######################################################
    @staticmethod
    def createUser(client:Client, sub="", name=""):
        mockSession = client.session
        mockSession["user"] = {"userinfo": {"sub": "", "nickname": "", "email": ""}}
        mockSession["user"]["userinfo"]["sub"] = "auth0|testuser" if sub == "" else sub
        mockSession["user"]["userinfo"]["nickname"] = "testuser" if name == "" else name
        mockSession["user"]["userinfo"]["email"] = "testuser@test.de"
        mockSession[SessionContent.USER_PERMISSIONS] = {"processes:read": "", "processes:files": "", "processes:messages": "", "processes:edit" : "", "processes:delete": "", "orga:edit": "", "orga:delete": "", "orga:read": "", "resources:read": "", "resources:edit": ""}
        mockSession[SessionContent.usertype] = "user"
        mockSession[SessionContent.INITIALIZED] = True
        mockSession[SessionContent.PG_PROFILE_CLASS] = ProfileClasses.user
        currentTime = datetime.datetime.now()
        mockSession["user"]["tokenExpiresOn"] = str(datetime.datetime(currentTime.year+1, currentTime.month, currentTime.day, currentTime.hour, currentTime.minute, currentTime.second, tzinfo=datetime.timezone.utc))
        mockSession.save()
        client.post("/"+paths["addUser"][0])
        return mockSession
    
    #######################################################
    @staticmethod
    def createProjectAndProcess(client:Client):
        projectObj = json.loads(client.get("/"+paths["createProjectID"][0]).content)
        processPathSplit = paths["createProcessID"][0].split("/")
        processPath = processPathSplit[0]+"/"+processPathSplit[1]+"/"+projectObj[ProjectDescription.projectID]+"/"
        processObj = json.loads(client.get("/"+processPath).content)
        return (projectObj, processObj)

    #######################################################
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.orgaClient = Client()
        self.createOrganization(self.orgaClient)

    # Tests!
    #######################################################
    def test_uploadAndDeleteModel(self):
        client = Client()
        self.createUser(client, self.test_uploadAndDeleteModel.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)

        # set service type
        changes = {"projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { "serviceType": 1}, "deletions":{} }
        response = client.patch("/"+paths["updateProcess"][0], json.dumps(changes))
        self.assertIs(response.status_code == 200, True)

        uploadBody = {ProjectDescription.projectID: projectObj[ProjectDescription.projectID], ProcessDescription.processID: processObj[ProcessDescription.processID], FileObjectContent.tags: "", FileObjectContent.licenses: "", FileObjectContent.certificates: "", "attachment": self.testFile}
        response = client.post("/"+paths["uploadModel"][0], uploadBody )
        self.assertIs(response.status_code == 200, True)
        getProjPathSplit = paths["getProject"][0].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(len(response[SessionContentSemperKI.processes][0][ProcessDescription.serviceDetails][ServiceDetails.model]) > 0, True)

        deleteModelPathSplit = paths["deleteModel"][0].split("/")
        deleteModelPath = deleteModelPathSplit[0] + "/" + deleteModelPathSplit[1] + "/" + processObj[ProcessDescription.processID] + "/"
        response = client.delete("/" + deleteModelPath)
        self.assertIs(response.status_code == 200, True)
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(ServiceDetails.model not in response[SessionContentSemperKI.processes][0][ProcessDescription.serviceDetails] , True)
