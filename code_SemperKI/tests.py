"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Tests for various functions and services
"""


from django.test import TestCase, Client
import datetime
import json, io
from .urls import paths

from Generic_Backend.code_General.definitions import SessionContent, UserDescription, OrganizationDescription, ProfileClasses
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
        #print("### Starting createProjectandProcess")
        projectObj = json.loads(client.post("/"+paths["createProjectID"][0], data= {"title": "my_title"}).content)
        #print("WE ARE HEREEEE!")
        #print(paths["createProjectID"])
        #print(f"projectObj: {projectObj}")
        #print("Survive cPaP 1")
        processPathSplit = paths["createProcessID"][0].split("/")
        #print("Survive cPaP 2")
        #print(f"processPathSplit: {processPathSplit}") #returns processPathSplit: ['public', 'process', 'create', '<str:projectID>', '']
        #print(f"projectObj.keys(): {projectObj.keys()}")
        #processPath = processPathSplit[0]+"/"+processPathSplit[1]+"/"+projectObj[ProjectDescription.projectID]+"/"
        processPath = processPathSplit[0]+"/"+processPathSplit[1]+"/"+processPathSplit[2]+"/"+projectObj[ProjectDescription.projectID]+"/" #schauen ob das wirklich passt (die [2])
        #print("Survive cPaP 3")
        processObj = json.loads(client.get("/"+processPath).content)
        #print(f"processObj: {processObj}")
        #print("Survive cPaP 4")
        return (projectObj, processObj)

    #######################################################
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.orgaClient = Client()
        self.createOrganization(self.orgaClient)

    # Tests!
    #######################################################
    def test_getProject(self): #works
        print("####Start test_getProject####")
        client = Client()
        self.createUser(client, self.test_getProject.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        getProjPathSplit = paths["getProject"][0].split("/")
        #print(f"getProjPathSplit: {getProjPathSplit}")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + getProjPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] +"/" #/get hinzugefügt
        #print(f"getProjPath: {getProjPath}")
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(response[ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True, f'{response[ProjectDescription.projectID]} != {projectObj[ProjectDescription.projectID]}')
        self.assertIs(response[SessionContentSemperKI.processes][0][ProcessDescription.processID] == processObj[ProcessDescription.processID], True, f'{response[SessionContentSemperKI.processes][0][ProcessDescription.processID]} != {processObj[ProcessDescription.processID]}')

        client.get("/"+paths["saveProjects"][0])
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(response[ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True, f'Expected projectID to be the same for response and projectObj. Instead got {response[ProjectDescription.projectID]} for response and {projectObj[ProjectDescription.projectID]} for projectObj')
        self.assertIs(response[SessionContentSemperKI.processes][0][ProcessDescription.processID] == processObj[ProcessDescription.processID], True, f'Expected processID to be the same for response and processObj. Instead got {response[SessionContentSemperKI.processes][0][ProcessDescription.processID]} for response and {processObj[ProcessDescription.processID]} for processObj')
        print("!!!!Success test_getProject!!!!")

    #######################################################
    def test_getFlatProjects(self): #works
        print("####Start test_getFlatProjects####")
        client = Client()
        self.createUser(client, self.test_getFlatProjects.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"][0][ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True, f'{response["projects"][0][ProjectDescription.projectID]} != {projectObj[ProjectDescription.projectID]}')

        client.get("/"+paths["saveProjects"][0])
        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"][0][ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True, f'{response["projects"][0][ProjectDescription.projectID]} != {projectObj[ProjectDescription.projectID]}')
        print("!!!!Success test_getFlatProjects!!!!")

    #######################################################
    def test_updateProject(self): #failure
        print("####Start test_updateProject####")
        client = Client()
        self.createUser(client, self.test_updateProject.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        changes = '{ "' + ProjectDescription.projectID + '": "' + projectObj[ProjectDescription.projectID] + '", "changes": { "' + ProjectDescription.projectDetails + '": {"title": "test"} } }'
        client.patch("/"+paths["updateProject"][0], changes)

        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        #self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        self.assertIs(response["projects"][0][ProjectDescription.projectDetails]["title"] == "test", True, f'got: {response["projects"][0][ProjectDescription.projectDetails]["title"]}') # no name set

        client.get("/"+paths["saveProjects"][0])

        changes = '{ "' + ProjectDescription.projectID + '": "' + projectObj[ProjectDescription.projectID] + '", "changes": { "' + ProjectDescription.projectDetails + '": {"title": "test2"} } }'
        client.patch("/"+paths["updateProject"][0], changes)
        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"][0][ProjectDescription.projectDetails]["title"] == "test2", True, f'got: {response["projects"][0][ProjectDescription.projectDetails]["title"]}')
        print("!!!!Success test_updateProject!!!!")

    #######################################################
    def test_deleteProjects(self): #works
        print("####Start test_deleteProjects####")
        client = Client()
        self.createUser(client, self.test_deleteProjects.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        #print("/"+paths["deleteProjects"][0]+"?projectIDs="+projectObj[ProjectDescription.projectID])
        #print("printed working deleteProjects path")
        response = client.delete("/"+paths["deleteProjects"][0]+"?projectIDs="+projectObj[ProjectDescription.projectID])
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"] == [], True, f'{response["projects"]}')

        projectObj, processObj = self.createProjectAndProcess(client)
        client.get("/"+paths["saveProjects"][0])
        response = client.delete("/"+paths["deleteProjects"][0]+"?projectIDs="+projectObj[ProjectDescription.projectID])
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"] == [], True, f'{response["projects"]}')
        print("!!!!Success test_deleteProjects!!!!")

    #######################################################
    def test_updateProcess(self): #failure
        print("####Start test_updateProcess####")
        client = Client()
        self.createUser(client, self.test_updateProcess.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        changes = {"projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { "serviceType": 1}, "deletions":{} }
        response = client.patch("/"+paths["updateProcess"][0], json.dumps(changes))
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}") #here

        client.get("/"+paths["saveProjects"][0])
        changes = {"projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { "processStatus": 1} }
        response = client.patch("/"+paths["updateProcess"][0], json.dumps(changes))
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        getProjPathSplit = paths["getProject"][0].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(response[SessionContentSemperKI.processes][0][ProcessDescription.serviceType] == 1, True, f'{response[SessionContentSemperKI.processes][0][ProcessDescription.serviceType]}')
        self.assertIs(response[SessionContentSemperKI.processes][0][ProcessDescription.processStatus] == 1, True, f'{response[SessionContentSemperKI.processes][0][ProcessDescription.processStatus]}')
        print("!!!!Success test_updateProcess!!!!")

    #######################################################
    def test_deleteProcesses(self): #works
        print("####Start test_deleteProcess####")
        client = Client()
        self.createUser(client, self.test_deleteProcesses.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)
        deletePathSplit = paths["deleteProcesses"][0].split("/")
        deletePath = deletePathSplit[0]+"/"+deletePathSplit[1]+"/"+deletePathSplit[2]+"/"+projectObj[ProjectDescription.projectID]+"/?processIDs=" + processObj[ProcessDescription.processID]
        response = client.delete("/"+deletePath)      
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        getProjPathSplit = paths["getProject"][0].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + getProjPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content) #here
        self.assertIs(len(response[SessionContentSemperKI.processes]) == 0, True, f'{len(response[SessionContentSemperKI.processes])}')

        projectObj, processObj = self.createProjectAndProcess(client)
        client.get("/"+paths["saveProjects"][0])
        deletePath = deletePathSplit[0]+"/"+deletePathSplit[1]+"/"+deletePathSplit[2]+"/"+projectObj[ProjectDescription.projectID]+"/?processIDs=" + processObj[ProcessDescription.processID]
        response = client.delete("/"+deletePath)
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + getProjPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(len(response[SessionContentSemperKI.processes]) == 0, True, f'{len(response[SessionContentSemperKI.processes])}')
        print("!!!!Success test_deleteProcesses!!!!")

    #######################################################
    def test_uploadAndDownloadFile(self): #Error
        print("####Starting test_uploadAndDownloadFile####")
        client = Client()
        #print("Survived client = Client() test_uploadAndDownloadFile")
        self.createUser(client, self.test_uploadAndDownloadFile.__name__)
        #print("Survived createUser in test_uploadAndDownloadFile")
        projectObj, processObj = self.createProjectAndProcess(client)
        #print("Survived createProjectAndProcess in test_uploadAndDownloadFile")
        uploadBody = {ProjectDescription.projectID: projectObj[ProjectDescription.projectID], ProcessDescription.processID: processObj[ProcessDescription.processID], "file": self.testFile, "origin": "my_origin"}
        response = client.post("/"+paths["uploadFiles"][0], uploadBody )
        self.assertIs(response.status_code == 200, True, f'got Statuscode {response.status_code}')
        getProjPathSplit = paths["getProject"][0].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + getProjPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content) 
        print(response[SessionContentSemperKI.processes][0].keys())  # fileID does not get Set here
        print(response[SessionContentSemperKI.processes][0]["imagePath"])
        print("HEEEEEEEEEEEEEEEEREEEEEEEEEEEEEEEEEEEEEEE")

        fileID = list(response[SessionContentSemperKI.processes][0][ProcessDescription.files].keys())[0] #error here, wrong key

        downloadPathSplit = paths["downloadFile"][0].split("/")
        downloadPath = downloadPathSplit[0] + "/" + downloadPathSplit[1] + "/" + downloadPathSplit[2] + "/" + downloadPathSplit[3] + "/" + projectObj[ProjectDescription.projectID] + "/" + processObj[ProcessDescription.processID] + "/" + fileID + "/"
        response = client.get("/"+downloadPath)
        with io.BytesIO(b"".join(response.streaming_content)) as buf_bytes:
            loaded_response_content = buf_bytes.read()
            self.testFile.seek(0)
            contentOfTestFile = self.testFile.read()
            self.assertIs(loaded_response_content == contentOfTestFile, True, f'{loaded_response_content} != {contentOfTestFile}')
        
        self.testFile.seek(0)
        # saved stuff
        #print(f"Saved stuff in test_uploadAndDownloadFile")
        projectObj, processObj = self.createProjectAndProcess(client)
        client.get("/"+paths["saveProjects"][0])
        uploadBody = {ProjectDescription.projectID: projectObj[ProjectDescription.projectID], ProcessDescription.processID: processObj[ProcessDescription.processID], "attachment": self.testFile}
        response = client.post("/"+paths["uploadFiles"][0], uploadBody )
        self.assertIs(response.status_code == 200, True, f'got Statuscode {response.status_code}')
        getProjPathSplit = paths["getProject"][0].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        fileID = list(response[SessionContentSemperKI.processes][0][ProcessDescription.files].keys())[0]

        downloadPathSplit = paths["downloadFile"][0].split("/")
        downloadPath = downloadPathSplit[0] + "/" + downloadPathSplit[1] + "/" + processObj[ProcessDescription.processID] + "/" + fileID + "/"
        response = client.get("/"+downloadPath)
        with io.BytesIO(b"".join(response.streaming_content)) as buf_bytes:
            loaded_response_content = buf_bytes.read()
            self.testFile.seek(0)
            contentOfTestFile = self.testFile.read()
            self.assertIs(loaded_response_content == contentOfTestFile, True, f'{loaded_response_content} != {contentOfTestFile}')
        print("!!!!Success test_UploadandDownloadFile!!!!")

        
        
    #######################################################
    def test_sendProject(self): #failure
        print("####Start test_sendProject####")
        client = Client()
        self.createUser(client, self.test_sendProject.__name__)
        projectObj, processObj = self.createProjectAndProcess(client)

        # set serviceType
        changes = { ProjectDescription.projectID: projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID] ], "changes": { ProcessUpdates.serviceType: 1} }
        response = client.patch("/"+paths["updateProcess"][0], json.dumps(changes))
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        # get Contractors for that service type
        getContractorsPathSplit = paths["getContractors"][0].split("/")
        getContractorsPath = getContractorsPathSplit[0] + "/" + getContractorsPathSplit[1] + "/" + processObj[ProcessDescription.processID] + "/"
        response = json.loads(client.get("/" + getContractorsPath).content)
        self.assertIs(len(response) > 0, True, f'{len(response)}')

        # set contractor
        changes = { ProjectDescription.projectID: projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { ProcessUpdates.provisionalContractor: response[0][OrganizationDescription.hashedID]} }
        response = client.patch("/"+paths["updateProcess"][0], json.dumps(changes))
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        # verify and send
        body = {ProjectDescription.projectID: projectObj[ProjectDescription.projectID], "send": True, "processIDs": [processObj[ProcessDescription.processID]]}
        response = client.patch("/"+paths["verifyProject"][0], json.dumps(body))
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        # get missed events of contractor
        response = json.loads(self.orgaClient.get("/"+paths["getMissedEvents"][0]).content)
        print(response)
        self.assertIs(response["events"][0][SessionContentSemperKI.processes][0][ProcessDescription.processStatus] > 0, True, f'{response["events"][0][SessionContentSemperKI.processes][0][ProcessDescription.processStatus]}') 
        print("!!!!Success test_sendProject!!!!")


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