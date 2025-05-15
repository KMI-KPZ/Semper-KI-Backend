"""
Part of Semper-KI software

Silvio Weging 2023
Lukas Hein 2024

Contains: Tests for various functions and services

"""


from django.test import TestCase, Client
import datetime
import json, io
from copy import deepcopy

from code_SemperKI.modelFiles.dataModel import DataDescription
from code_SemperKI.states.stateDescriptions import ProcessStatusAsString
from code_SemperKI.urls import paths


from Generic_Backend.code_General.definitions import SessionContent, UserDescription, OrganizationDescription, ProfileClasses
from .definitions import ProjectDescription, ProcessDescription, SessionContentSemperKI, ProcessUpdates

# Create your tests here.

#######################################################
class TestProjects(TestCase):
    testFile = io.BytesIO(b'binary stl file                                                                \x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x80\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x00\x00\x80\xbf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\\\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00 B\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\xa0A\x00\x00\x0c\xc2\x00\x00 B\x00\x00\x00\x00\x00\x00\x0c\xc2\x00\x00pB\x00\x00\x00\x00\x00\x00')

    # not part of the tests!
    #######################################################
    @classmethod
    def fileFactory(self) -> io.BytesIO:
        """
        Return a copy of the testfile
        
        """
        return deepcopy(self.testFile)

    #######################################################
    @classmethod
    def createOrganization(self, client:Client):
        mockSession = client.session
        mockSession[SessionContent.MOCKED_LOGIN] = True
        mockSession[SessionContent.IS_PART_OF_ORGANIZATION] = True
        mockSession[SessionContent.PG_PROFILE_CLASS] = "organization"
        mockSession[SessionContent.usertype] = "organization"
        mockSession[SessionContent.PATH_AFTER_LOGIN] = "127.0.0.1:3000" # no real use but needs to be set
        mockSession.save()
        client.get("/"+paths["callbackLogin"][0])
        client.patch("/"+paths["updateDetailsOfOrga"][0], data={"changes": { "supportedServices": [1] } }, content_type="application/json")
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
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.orgaClient = Client()
        self.createOrganization(self.orgaClient)

    # Tests!
    #######################################################
    def test_getProject(self):
        client = Client()
        projectObj, processObj = self.createProjectAndProcess(client)
        getProjPathSplit = paths["getProject"][0].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + getProjPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(response[ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True, f'{response[ProjectDescription.projectID]} != {projectObj[ProjectDescription.projectID]}')
        self.assertIs(response[SessionContentSemperKI.processes][0][ProcessDescription.processID] == processObj[ProcessDescription.processID], True, f'{response[SessionContentSemperKI.processes][0][ProcessDescription.processID]} != {processObj[ProcessDescription.processID]}')

        self.createUser(client)
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(response[ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True, f'Expected projectID to be the same for response and projectObj. Instead got {response[ProjectDescription.projectID]} for response and {projectObj[ProjectDescription.projectID]} for projectObj')
        self.assertIs(response[SessionContentSemperKI.processes][0][ProcessDescription.processID] == processObj[ProcessDescription.processID], True, f'Expected processID to be the same for response and processObj. Instead got {response[SessionContentSemperKI.processes][0][ProcessDescription.processID]} for response and {processObj[ProcessDescription.processID]} for processObj')

    #######################################################
    def test_getFlatProjects(self):
        client = Client()
        projectObj, processObj = self.createProjectAndProcess(client)
        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"][0][ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True, f'{response["projects"][0][ProjectDescription.projectID]} != {projectObj[ProjectDescription.projectID]}')

        self.createUser(client)
        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"][0][ProjectDescription.projectID] == projectObj[ProjectDescription.projectID], True, f'{response["projects"][0][ProjectDescription.projectID]} != {projectObj[ProjectDescription.projectID]}')

    #######################################################
    def test_updateProject(self):
        client = Client()
        projectObj, processObj = self.createProjectAndProcess(client)
        changes = '{ "' + ProjectDescription.projectID + '": "' + projectObj[ProjectDescription.projectID] + '", "changes": { "' + ProjectDescription.projectDetails + '": {"title": "test"} } }'
        response = client.patch("/"+paths["updateProject"][0], changes, content_type="application/json")
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"][0][ProjectDescription.projectDetails]["title"] == "test", True, f'got: {response["projects"][0][ProjectDescription.projectDetails]["title"]}')

        self.createUser(client)

        changes = '{ "' + ProjectDescription.projectID + '": "' + projectObj[ProjectDescription.projectID] + '", "changes": { "' + ProjectDescription.projectDetails + '": {"title": "test2"} } }'
        client.patch("/"+paths["updateProject"][0], changes, content_type="application/json")
        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"][0][ProjectDescription.projectDetails]["title"] == "test2", True, f'got: {response["projects"][0][ProjectDescription.projectDetails]["title"]}')

    #######################################################
    def test_deleteProjects(self):
        client = Client()
        projectObj, processObj = self.createProjectAndProcess(client)
        response = client.delete("/"+paths["deleteProjects"][0]+"?projectIDs="+projectObj[ProjectDescription.projectID])
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"] == [], True, f'{response["projects"]}')

        self.createUser(client)
        projectObj, processObj = self.createProjectAndProcess(client)
        response = client.delete("/"+paths["deleteProjects"][0]+"?projectIDs="+projectObj[ProjectDescription.projectID])
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        response = json.loads(client.get("/"+paths["getFlatProjects"][0]).content)
        self.assertIs(response["projects"] == [], True, f'{response["projects"]}')

    #######################################################
    def test_updateProcess(self):
        client = Client()
        
        projectObj, processObj = self.createProjectAndProcess(client)
        changes = {"projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { "serviceType": 1}, "deletions":{} }
        response = client.patch("/"+paths["updateProcess"][0], json.dumps(changes),  content_type="application/json")
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        self.createUser(client)
        changes = {"projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { "processStatus": 1} }
        response = client.patch("/"+paths["updateProcess"][0], json.dumps(changes), content_type="application/json")
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        getProcPathSplit = paths["getProcess"][0].split("/")
        getProcPath = getProcPathSplit[0] + "/" + getProcPathSplit[1] + "/" + getProcPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] + "/" + processObj[ProcessDescription.processID] + "/"
        response = json.loads(client.get("/"+getProcPath).content)
        self.assertIs(response[ProcessDescription.serviceType] == 1, True, f'{response[ProcessDescription.serviceType]}')
        self.assertIs(response[ProcessDescription.processStatus] == 1, False, f'processStatus should not get changed anymore{response[ProcessDescription.processStatus]}')

    #######################################################
    def test_deleteProcesses(self):
        client = Client()
        
        projectObj, processObj = self.createProjectAndProcess(client)
        deletePathSplit = paths["deleteProcesses"][0].split("/")
        deletePath = deletePathSplit[0]+"/"+deletePathSplit[1]+"/"+deletePathSplit[2]+"/"+projectObj[ProjectDescription.projectID]+"/?processIDs=" + processObj[ProcessDescription.processID]
        response = client.delete("/"+deletePath)      
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        getProjPathSplit = paths["getProject"][0].split("/")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + getProjPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(len(response[SessionContentSemperKI.processes]) == 0, True, f'{len(response[SessionContentSemperKI.processes])}')

        self.createUser(client)
        projectObj, processObj = self.createProjectAndProcess(client)
        deletePath = deletePathSplit[0]+"/"+deletePathSplit[1]+"/"+deletePathSplit[2]+"/"+projectObj[ProjectDescription.projectID]+"/?processIDs=" + processObj[ProcessDescription.processID]
        response = client.delete("/"+deletePath)
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        getProjPath = getProjPathSplit[0] + "/" + getProjPathSplit[1] + "/" + getProjPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] +"/"
        response = json.loads(client.get("/"+getProjPath).content)
        self.assertIs(len(response[SessionContentSemperKI.processes]) == 0, True, f'{len(response[SessionContentSemperKI.processes])}')

    #######################################################
    def test_uploadAndDownloadFile(self):
        client = Client()
        
        projectObj, processObj = self.createProjectAndProcess(client)
        localCopyOfTestFile = self.fileFactory()
        uploadBody = {ProjectDescription.projectID: projectObj[ProjectDescription.projectID], ProcessDescription.processID: processObj[ProcessDescription.processID], "file": localCopyOfTestFile, "origin": "my_origin"}
        response = client.post("/"+paths["uploadFiles"][0], uploadBody )
        self.assertIs(response.status_code == 200, True, f'got Statuscode {response.status_code}')
        getProcPathSplit = paths["getProcess"][0].split("/")
        getProcPath = getProcPathSplit[0] + "/" + getProcPathSplit[1] + "/" + getProcPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] + "/" + processObj[ProcessDescription.processID] + "/"
        response = json.loads(client.get("/"+getProcPath).content)

        fileID = list(response[ProcessDescription.files].keys())[0]

        downloadPathSplit = paths["downloadFile"][0].split("/")
        downloadPath = downloadPathSplit[0] + "/" + downloadPathSplit[1] + "/" + downloadPathSplit[2] + "/" + downloadPathSplit[3] + "/" + projectObj[ProjectDescription.projectID] + "/" + processObj[ProcessDescription.processID] + "/" + fileID + "/"
        response = client.get("/"+downloadPath)
        with io.BytesIO(b"".join(response.streaming_content)) as buf_bytes:
            loaded_response_content = buf_bytes.read()
            localCopyOfTestFile.seek(0)
            contentOfTestFile = localCopyOfTestFile.read()
            self.assertIs(loaded_response_content == contentOfTestFile, True, f'{loaded_response_content} != {contentOfTestFile}')
        
        localCopyOfTestFile.seek(0)
        # saved stuff
        self.createUser(client)
        projectObj, processObj = self.createProjectAndProcess(client)
        uploadBody = {ProjectDescription.projectID: projectObj[ProjectDescription.projectID], ProcessDescription.processID: processObj[ProcessDescription.processID], "attachment": localCopyOfTestFile, "origin": "my_origin"}
        response = client.post("/"+paths["uploadFiles"][0], uploadBody )
        self.assertIs(response.status_code == 200, True, f'got Statuscode {response.status_code}')
        getProcPathSplit = paths["getProcess"][0].split("/")
        getProcPath = getProcPathSplit[0] + "/" + getProcPathSplit[1] + "/" + getProcPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] + "/" + processObj[ProcessDescription.processID] + "/"
        response = json.loads(client.get("/"+getProcPath).content)
        fileID = list(response[ProcessDescription.files].keys())[0]

        downloadPathSplit = paths["downloadFile"][0].split("/")
        downloadPath = downloadPathSplit[0] + "/" + downloadPathSplit[1] + "/" + downloadPathSplit[2] + "/" + downloadPathSplit[3] + "/" + projectObj[ProjectDescription.projectID] + "/" + processObj[ProcessDescription.processID] + "/" + fileID + "/"
        response = client.get("/"+downloadPath)
        with io.BytesIO(b"".join(response.streaming_content)) as buf_bytes:
            loaded_response_content = buf_bytes.read()
            localCopyOfTestFile.seek(0)
            contentOfTestFile = localCopyOfTestFile.read()
            self.assertIs(loaded_response_content == contentOfTestFile, True, f'{loaded_response_content} != {contentOfTestFile}')

    ##################################################
    def test_processHistory(self):
        client = Client()

        # Create user, project and process
        self.createUser(client)
        projectObj, processObj = self.createProjectAndProcess(client)
        # call getProcessHistory as get with processID in path
        historyPath = paths["getProcessHistory"][0].split("/")
        historyPath = historyPath[0] + "/" + historyPath[1] + "/" + historyPath[2] + "/"+ historyPath[3] + "/" + processObj[ProcessDescription.processID] + "/"
        response = client.get("/"+historyPath)
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")
        response = json.loads(response.content)
        # Check return value for length of history
        self.assertIs(len(response["history"])>=1, True, f'{len(response["history"])} < 1')

        # save stuff
        self.createUser(client)
        # call getProcessHistory as get with processID in path
        historyPath = paths["getProcessHistory"][0].split("/")
        historyPath = historyPath[0] + "/" + historyPath[1] + "/" + historyPath[2] + "/" + historyPath[3] + "/" + processObj[ProcessDescription.processID] + "/"
        response = json.loads(client.get("/"+historyPath).content)
        # Check return value for length of history
        self.assertIs(len(response["history"])>=1, True, f'{len(response["history"])} < 1')



    ##################################################
    def test_stateMachine(self):
        client = Client()

        # create project and process but no user as it's not necessary
        projectObj, processObj = self.createProjectAndProcess(client)

        # call updateProcess with selected service 1
        changes = {"projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]], "changes": { "serviceType": 1}, "deletions":{} }
        response = client.patch("/"+paths["updateProcess"][0], json.dumps(changes), content_type="application/json")
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        # call getProcess and get buttons
        getProcPathSplit = paths["getProcess"][0].split("/")
        getProcPath = getProcPathSplit[0] + "/" + getProcPathSplit[1] + "/" + getProcPathSplit[2] + "/" + projectObj[ProjectDescription.projectID] + "/" + processObj[ProcessDescription.processID] + "/"
        response = json.loads(client.get("/"+getProcPath).content)
        self.assertIs(response[ProcessDescription.serviceType] == 1, True, f'{response[ProcessDescription.serviceType]}')

        self.assertIs("processStatusButtons" in response and len(response["processStatusButtons"]) > 0 and "action" in response["processStatusButtons"][0], True, f'{response}')
        buttonData = response["processStatusButtons"][0]["action"]["data"]

        # "press" Button BACK-TO-DRAFT by calling a POST to statusButtonRequest
        button = {"buttonData":buttonData, "projectID": projectObj[ProjectDescription.projectID], "processIDs": [processObj[ProcessDescription.processID]]}
        response = client.post("/"+paths["statusButtonRequest"][0], json.dumps(button), content_type="application/json")
        self.assertIs(response.status_code == 200, True, f"got: {response.status_code}")

        # call getProcess and check if processStatus code is correct (see StateDescription for the integer value)
        response = json.loads(client.get("/"+getProcPath).content)
        self.assertIs(response[ProcessDescription.processStatus] == 0, True, f'{response[ProcessDescription.processStatus]}')


