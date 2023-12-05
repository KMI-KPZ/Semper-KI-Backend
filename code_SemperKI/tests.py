"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Tests for various functions and services
"""


from django.test import TestCase, Client
import datetime
import json, io
from .urls import paths

from code_General.definitions import SessionContent, UserDescription, OrganizationDescription, ProfileClasses
from .definitions import ProjectDescription, ProcessDescription, SessionContentSemperKI, ProcessUpdates

# Create your tests here.

#######################################################
class TestProjects(TestCase):
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
        client.post("/"+paths["addOrga"])
        client.post("/"+paths["addUser"])
        client.patch("/"+paths["updateDetailsOfOrga"], '{"data": {"content": { "supportedServices": [1] } } }')
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
        client.post("/"+paths["addUser"])
        return mockSession
    
    #######################################################
    @staticmethod
    def createProjectAndProcess(client:Client):
        projectObj = json.loads(client.get("/"+paths["createProjectID"]).content)
        processPathSplit = paths["createProcessID"].split("/")
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
    def test_getProject(self):
        client = Client()
        self.createUser(client, self.test_getProject.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        getProjPathSplit = paths["getProject"].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(response[ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True)
        self.assertIs(response[SessionContentSemperKI.processes][0][ProcessDescription.processID] == processObj[ProcessDescription.processID], True)

        client.get("/"+paths["saveProjects"])
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(response[ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True)
        self.assertIs(response[SessionContentSemperKI.processes][0][ProcessDescription.processID] == processObj[ProcessDescription.processID], True)


    #######################################################
    def test_getFlatProjects(self):
        client = Client()
        self.createUser(client, self.test_getFlatProjects.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        response = json.loads(client.get("/"+paths["getFlatProjects"]).content)
        self.assertIs(response["projects"][0][ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True)

        client.get("/"+paths["saveProjects"])
        response = json.loads(client.get("/"+paths["getFlatProjects"]).content)
        self.assertIs(response["projects"][0][ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True)

    #######################################################
    def test_updateProject(self):
        client = Client()
        self.createUser(client, self.test_updateProject.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        changes = '{ "' + ProjectDescription.projectID + '": "' + projectObj[ProjectDescription.projectID] + '", "changes": { "' + ProjectDescription.details + '": {"name": "test"} } }'
        client.patch("/"+paths["updateProject"], changes)

        response = json.loads(client.get("/"+paths["getFlatProjects"]).content)
        self.assertIs(response["projects"][0][ProjectDescription.details]["name"] == "test", True)

        client.get("/"+paths["saveProjects"])

        changes = '{ "' + ProjectDescription.projectID + '": "' + projectObj[ProjectDescription.projectID] + '", "changes": { "' + ProjectDescription.details + '": {"name": "test2"} } }'
        client.patch("/"+paths["updateProject"], changes)
        response = json.loads(client.get("/"+paths["getFlatProjects"]).content)
        self.assertIs(response["projects"][0][ProjectDescription.details]["name"] == "test2", True)

    #######################################################
    def test_deleteProjects(self):
        client = Client()
        self.createUser(client, self.test_deleteProjects.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        response = client.delete("/"+paths["deleteProjects"]+"?projectIDs="+projectObj[ProjectDescription.projectID])
        self.assertIs(response.status_code == 200, True)
        response = json.loads(client.get("/"+paths["getFlatProjects"]).content)
        self.assertIs(response["projects"] == [], True)

        projectObj, processObj = self.createProjectAndProcess(client)
        client.get("/"+paths["saveProjects"])
        response = client.delete("/"+paths["deleteProjects"]+"?projectIDs="+projectObj[ProjectDescription.projectID])
        self.assertIs(response.status_code == 200, True)
        response = json.loads(client.get("/"+paths["getFlatProjects"]).content)
        self.assertIs(response["projects"] == [], True)


    #######################################################
    def test_updateProcess(self):
        client = Client()
        self.createUser(client, self.test_updateProcess.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        changes = {"projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { "serviceType": 1}, "deletions":{} }
        response = client.patch("/"+paths["updateProcess"], json.dumps(changes))
        self.assertIs(response.status_code == 200, True)

        client.get("/"+paths["saveProjects"])
        changes = {"projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { "processStatus": 1} }
        response = client.patch("/"+paths["updateProcess"], json.dumps(changes))
        self.assertIs(response.status_code == 200, True)

        getProjPathSplit = paths["getProject"].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(response[SessionContentSemperKI.processes][0][ProcessDescription.serviceType] == 1, True)
        self.assertIs(response[SessionContentSemperKI.processes][0][ProcessDescription.processStatus] == 1, True)

    #######################################################
    def test_deleteProcesses(self):
        client = Client()
        self.createUser(client, self.test_deleteProcesses.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        deletePathSplit = paths["deleteProcesses"].split("/")
        deletePath = deletePathSplit[0]+"/"+deletePathSplit[1]+"/"+projectObj[ProjectDescription.projectID]+"/?processIDs=" + processObj[ProcessDescription.processID]
        response = client.delete("/"+deletePath)      
        self.assertIs(response.status_code == 200, True)
        getProjPathSplit = paths["getProject"].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(len(response[SessionContentSemperKI.processes]) == 0, True)

        projectObj, processObj = self.createProjectAndProcess(client)
        client.get("/"+paths["saveProjects"])
        deletePath = deletePathSplit[0]+"/"+deletePathSplit[1]+"/"+projectObj[ProjectDescription.projectID]+"/?processIDs=" + processObj[ProcessDescription.processID]
        response = client.delete("/"+deletePath)
        self.assertIs(response.status_code == 200, True)
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(len(response[SessionContentSemperKI.processes]) == 0, True)

    #######################################################
    def test_uploadAndDownloadFile(self):
        client = Client()
        self.createUser(client, self.test_uploadAndDownloadFile.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        uploadBody = {ProjectDescription.projectID: projectObj[ProjectDescription.projectID], ProcessDescription.processID: processObj[ProcessDescription.processID], "attachment": self.testFile}
        response = client.post("/"+paths["uploadFiles"], uploadBody )
        self.assertIs(response.status_code == 200, True)
        getProjPathSplit = paths["getProject"].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        fileID = list(response[SessionContentSemperKI.processes][0][ProcessDescription.files].keys())[0]

        downloadPathSplit = paths["downloadFile"].split("/")
        downloadPath = downloadPathSplit[0] + "/" + downloadPathSplit[1] + "/" + processObj[ProcessDescription.processID] + "/" + fileID + "/"
        response = client.get("/"+downloadPath)
        with io.BytesIO(b"".join(response.streaming_content)) as buf_bytes:
            loaded_response_content = buf_bytes.read()
            self.testFile.seek(0)
            contentOfTestFile = self.testFile.read()
            self.assertIs(loaded_response_content == contentOfTestFile, True)

        # TODO repeat for saved stuff
        
    #######################################################
    def test_sendProject(self):
        client = Client()
        self.createUser(client, self.test_sendProject.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)

        # set serviceType
        changes = { ProjectDescription.projectID: projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID] ], "changes": { ProcessUpdates.serviceType: 1} }
        response = client.patch("/"+paths["updateProcess"], json.dumps(changes))
        self.assertIs(response.status_code == 200, True)

        # # get Contractors for that service type
        getContractorsPathSplit = paths["getContractors"].split("/")
        getContractorsPath = getContractorsPathSplit[0] + "/" + getContractorsPathSplit[1] + "/" + processObj[ProcessDescription.processID] + "/"
        response = json.loads(client.get("/" + getContractorsPath).content)
        self.assertIs(len(response) > 0, True)

        # # set contractor
        changes = { ProjectDescription.projectID: projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { ProcessUpdates.provisionalContractor: response[0][OrganizationDescription.hashedID]} }
        response = client.patch("/"+paths["updateProcess"], json.dumps(changes))
        self.assertIs(response.status_code == 200, True)

        # # verify and send
        body = {ProjectDescription.projectID: projectObj[ProjectDescription.projectID], "send": True, "processIDs": [processObj[ProcessDescription.processID]]}
        response = client.patch("/"+paths["verifyProject"], json.dumps(body))
        self.assertIs(response.status_code == 200, True)

        # # get missed events of contractor
        response = json.loads(self.orgaClient.get("/"+paths["getMissedEvents"]).content)
        print(response)
        self.assertIs(response["events"][0][SessionContentSemperKI.processes][0]["status"] > 0, True)


# class TestFilters(TestCase):
#     filters = {"filters": [{"id": 0, "isChecked": False, "isOpen": False, "question": {"isSelectable": True, "title": "costs", "category": "general", "type": "slider", "range": [0, 9999], "values": "null", "units": "\u20ac"}, "answer": "null"}]}

#     def testGetFilters(self):
#         # send via POST as body to getFilters
#         returnedJson = self.client.post("/"+paths["getFilters"], content_type="application/json", data=self.filters)
#         # if json is as expected, it worked
#         returnedJsonAsDict = json.loads(returnedJson.content)
#         self.assertIs(len(returnedJsonAsDict["filters"]) == 1, True) #TODO

#     def testGetPostProcessing(self):
#         # send via POST as body to getPostProcessing
#         returnedJson = self.client.post("/"+paths["getPostProcessing"], content_type="application/json", data=self.filters)
#         # if json is as expected and contains postProcessing stuff, it worked
#         returnedJsonAsDict = json.loads(returnedJson.content)
#         self.assertIs(len(returnedJsonAsDict["postProcessing"]) >= 1, True)
#         pass

#     def testGetMaterials(self):
#         # send via POST as body to getMaterials
#         returnedJson = self.client.post("/"+paths["getMaterials"], content_type="application/json", data=self.filters)
#         # if json is as expected and contains materials stuff, it worked
#         returnedJsonAsDict = json.loads(returnedJson.content)
#         self.assertIs(len(returnedJsonAsDict["materials"]) >= 1, True)
#         pass

#     def testGetModels(self):
#         # send via POST as body to getModels
#         returnedJson = self.client.post("/"+paths["getModels"], content_type="application/json", data=self.filters)
#         # if json is as expected and contains models stuff, it worked
#         returnedJsonAsDict = json.loads(returnedJson.content)
#         self.assertIs(len(returnedJsonAsDict["models"]) >= 1, True)
#         pass