"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Offers an interface to access the session dictionary in a structured way
"""

from django.utils import timezone
import logging, copy

from Generic_Backend.code_General.definitions import GlobalDefaults, SessionContent, FileObjectContent
from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.connections.postgresql.pgProfiles import profileManagement, ProfileManagementUser
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn
from Generic_Backend.code_General.utilities import crypto

from ...definitions import PriorityTargetsSemperKI, SessionContentSemperKI, MessageInterfaceFromFrontend, DataType
from ...definitions import ProjectUpdates, ProcessUpdates, ProcessDetails, ProjectOutput
from ...modelFiles.processModel import ProcessInterface, ProcessDescription
from ...modelFiles.projectModel import ProjectInterface, ProjectDescription
from ...modelFiles.dataModel import DataInterface, DataDescription
from ...serviceManager import serviceManager
import code_SemperKI.states.stateDescriptions as StateDescriptions
from .abstractInterface import AbstractContentInterface

logger = logging.getLogger("errors")

#######################################################
class StructuredSession():
    """
    Interface class that handles the session content

    """

    currentSession : dict = {}

#######################################################
    def __init__(self, session) -> None:
        """
        Initialize with existing session
        
        """

        self.currentSession = session
    
    #######################################################
    def getSession(self):
        """
        Return current session
        
        """
        return self.currentSession
    
    #######################################################
    def getIfContentIsInSession(self) -> bool:
        """
        Tell whether there is content in the session

        :return: if there are projects in the session, use these and tell the this
        :rtype: bool
        
        """

        return True if SessionContentSemperKI.CURRENT_PROJECTS in self.currentSession else False

    #######################################################
    def clearContentFromSession(self) -> None:
        """
        Delete all projects from session

        :return: Nothing
        :rtype: None
        
        """
        self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS].clear()
        del self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS]
        self.currentSession.modified = True

    #######################################################
    def getProject(self, projectID:str) -> dict:
        """
        Return specific project from session

        :param projectID: The ID of the project
        :type projectID: str
        :return: Dictionary with project in it
        :rtype: dict

        """
        if projectID in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS]:
            return self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]
        else:
            return {}

    #######################################################
    def getProjects(self) -> list:
        """
        Return all projects from session

        :return: list with projects in it
        :rtype: list

        """

        return list(self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS].values())
    
    #######################################################
    def setProject(self, projectID:str, content:dict) -> None:
        """
        Set content of project in session

        :param projectID: The ID of the project
        :type projectID: str
        :param content: What the project should consist of
        :type content: dict
        :return: Nothing
        :rtype: None
        """

        if SessionContentSemperKI.CURRENT_PROJECTS not in self.currentSession:
            self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS] = {}
        
        self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID] = content

    #######################################################
    def deleteProject(self, projectID:str):
        """
        Delete the project

        :param projectID: The ID of the project
        :type projectID: str
        :return: Nothing
        :rtype: None
        """

        del self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]

    #######################################################
    def getProcesses(self, projectID:str):
        """
        Return the process from session

        :param projectID: The ID of the project
        :type projectID: str
        :return: dict of process
        :rtype: dict

        """
        if SessionContentSemperKI.processes in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]:
            return self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes]
        else:
            return {}
###################################################################
    #######################################################
    def getProcess(self, projectID:str, processID:str):
        """
        Return the process from session

        :param projectID: The ID of the project
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :return: Dictionary with process in it
        :rtype: Dict

        """
        if SessionContentSemperKI.processes in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]:
            return self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID]
        else:
            return {}
    #######################################################
    def getProcessPerID(self, processID:str):
        """
        Get process without project ID

        :param processID: The ID of the process
        :type processID: str
        :return: Dictionary with process in it
        :rtype: dict
        
        """
        for projectID in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS]:
            if SessionContentSemperKI.processes in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]:
                for currentProcessID in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes]:
                    if currentProcessID == processID:
                        return self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID]

        return {}
    
    #######################################################
    def getProcessAndProjectPerID(self, processID:str):
        """
        Get process without project ID but return it

        :param processID: The ID of the process
        :type processID: str
        :return: Corresponding projectID and dictionary with process in it
        :rtype: (str,dict)
        
        """
        for projectID in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS]:
            if SessionContentSemperKI.processes in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]:
                for currentProcessID in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes]:
                    if currentProcessID == processID:
                        return (projectID, self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID])

        return (None, None)

    #######################################################
    def setProcess(self, projectID:str, processID:str, content:dict):
        """
        Set content of process in session

        :param projectID: The ID of the project
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :param content: What the process should consist of
        :type content: dict
        :return: Nothing
        :rtype: None
        """
        if SessionContentSemperKI.processes not in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]:
            self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes] = {}

        self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID] = content

    #######################################################
    def deleteProcess(self, processID:str):
        """
        Delete one specific process

        :param processID: The ID of the process
        :type processID: str
        :return: Nothing
        :rtype: None
        
        """
        for projectID in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS]:
            if SessionContentSemperKI.processes in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]:
                for currentProcessID in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes]:
                    if currentProcessID == processID:
                        del self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][currentProcessID]
                        break



#######################################################
class ProcessManagementSession(AbstractContentInterface):
    """
    Offers an interface equal to that of the postgres, albeit session based
    
    """

    #######################################################
    def __init__(self, session) -> None:
        self.structuredSessionObj = StructuredSession(session)

    #######################################################
    def getSession(self):
        """
        Get the session
        
        :return: The session 
        :rtype: Django session obj (dict)
        """
        return self.structuredSessionObj.getSession()


    ##############################################
    def getUserID(self) -> str:
        """
        Retrieve UserID from session
        
        :return: UserID
        :rtype: str
        """

        return GlobalDefaults.anonymous
        
    ##############################################
    def getActualUserID(self) -> str:
        """
        Retrieve the user behind the organization
        
        :return: UserID
        :rtype: str
        """

        return GlobalDefaults.anonymous
        
    ##################################################
    def checkIfUserIsClient(self, userHashID, projectID="", processID=""):
        """
        See if the user is the client of either the project or the process

        :param userHashID: The hashed ID of the user/organization
        :type userHashID: str
        :param projectID: The ID of the project
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :return: True if user is client, false if not
        :rtype: bool
        """
        if projectID:
            project = self.structuredSessionObj.getProject(projectID)
            return project[ProjectDescription.client] == userHashID
        if processID:
            projectID, process = self.structuredSessionObj.getProcessAndProjectPerID(processID)
            return process[ProcessDescription.client] == userHashID
        return False    
    
    #######################################################
    def getData(self, processID, processObj=None):
        """
        Get all data entries for a process

        :param processID: The ID of the process
        :type processID: str
        :return: List of data entries
        :rtype: list
        """
        try:
            outList = []
            for entry in self.structuredSessionObj.currentSession['data_history']:
                if entry[DataDescription.processID] == processID:
                    outList.append(entry)
            return outList
        except (Exception) as error:
            logger.error(f'Generic error in getData: {str(error)}')

        return []

    #######################################################
    def getDataWithContentID(self, processID, contentID):
        """
        Get data entries for a process with a specific content ID

        :param processID: The ID of the process
        :type processID: str
        :param contentID: The content ID to search for
        :type contentID: str
        :return: List of matching data entries
        :rtype: list
        """
        data = self.structuredSessionObj.currentSession['data_history']
        return [entry for entry in data if entry.get('contentID') == contentID]
    
    #######################################################
    def getDataWithID(self, processID, dataID):
        """
        Get a specific data entry for a process

        :param processID: The ID of the process
        :type processID: str
        :param dataID: The data ID to search for
        :type dataID: str
        :return: The matching data entry or None
        :rtype: dict or None
        """
        data = self.structuredSessionObj.currentSession['data_history']
        return next((entry for entry in data if entry.get('dataID') == dataID), None)
    
    #######################################################
    def getDataByType(self, processID, dataType):
        """
        Get data entries for a process of a specific type

        :param processID: The ID of the process
        :type processID: str
        :param dataType: The data type to search for
        :type dataType: DataType
        :return: List of matching data entries
        :rtype: list
        """
        data = self.structuredSessionObj.currentSession['data_history']
        return [entry for entry in data if entry.get('dataType') == dataType]
    
    #######################################################
    def getIfContentIsInSession(self) -> bool:
        """
        Tell management class whether there is content in the session

        :return: if there are projects in the session, use these and tell the management class this
        :rtype: bool
        
        """

        return self.structuredSessionObj.getIfContentIsInSession()

    #######################################################
    def getProjectObj(self, projectID:str):
        """
        Return the project and all its details

        :param projectID: The ID of the project
        :type projectID: str
        :return: Project Object
        :rtype: ProjectInterface
        
        """
        try:
            content = self.structuredSessionObj.getProject(projectID)
            returnObj = ProjectInterface(projectID, content[ProjectDescription.createdWhen], content[ProjectDescription.client])
            returnObj.setValues(content[ProjectDescription.projectStatus], content[ProjectDescription.client], content[ProjectDescription.projectDetails], content[ProjectDescription.updatedWhen], content[ProjectDescription.accessedWhen])
            return returnObj
        except (Exception) as error:
            logger.error(f"Could not get project object: {str(error)}")
            return None

    #######################################################
    def createProject(self, projectID:str, client:str):
        """
        Create the project

        :param projectID: The ID of the project
        :type projectID: str
        :param client: anonymous client, necessary for interface
        :type client: str
        :return: Nothing
        :rtype: None
        
        """
        now = timezone.now()

        self.structuredSessionObj.setProject(projectID, ProjectInterface(projectID, str(now), client).toDict())
    
    #######################################################
    def getProject(self, projectID:str) -> dict:
        """
        Get info about one project.

        :param projectID: ID of the project
        :type projectID: str
        :return: dict with info about that project
        :rtype: dict

        """
        try: 
            savedProject = copy.deepcopy(self.structuredSessionObj.getProject(projectID))
            savedProject[SessionContentSemperKI.processes] = [savedProject[SessionContentSemperKI.processes][process] for process in savedProject[SessionContentSemperKI.processes]]
            return savedProject
        
        except (Exception) as error:
            logger.error(f'could not get project: {str(error)}')
            return error
        
    ##############################################
    def updateProject(self, projectID:str, updateType: ProjectUpdates, content:dict):
        """
        Change details of an project like its status. 

        :param projectID: project ID that this project belongs to
        :type projectID: str
        :param updateType: changed project details
        :type updateType: EnumUpdates
        :param content: changed project, can be many stuff
        :type content: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            if updateType == ProjectUpdates.projectStatus:
                currentProject = self.structuredSessionObj.getProject(projectID)
                currentProject[ProjectDescription.projectStatus] = content
                currentProject[ProjectDescription.updatedWhen] = updated

            elif updateType == ProjectUpdates.projectDetails:
                currentProject = self.structuredSessionObj.getProject(projectID)
                for key in content:
                    currentProject[ProjectDescription.projectDetails][key] = content[key]
                currentProject[ProjectDescription.updatedWhen] = str(updated)
            return True
        except (Exception) as error:
            logger.error(f'could not update project: {str(error)}')
            return error

    #######################################################
    def deleteProject(self, projectID:str):
        """
        Delete specific project.

        :param projectID: unique project ID to be deleted
        :type projectID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        try:
            processes = self.structuredSessionObj.getProcesses(projectID)
            for currentProcess in processes:
                files = processes[currentProcess][ProcessDescription.files]
                for fileKey in files:
                    if FileObjectContent.isFile not in files[fileKey] or files[fileKey][FileObjectContent.isFile]:
                        if files[fileKey][FileObjectContent.remote]:
                            s3.manageRemoteS3.deleteFile(files[fileKey][FileObjectContent.path])
                        else:
                            s3.manageLocalS3.deleteFile(files[fileKey][FileObjectContent.path])
            self.structuredSessionObj.deleteProject(projectID)
        except (Exception) as error:
            logger.error(f'could not delete project: {str(error)}')
            return error

    ##############################################
    def getProjectsFlat(self, session):
        """
        Get all projects for that user but with limited detail.

        :param session: session of that user, not used here
        :type session: dict
        :return: sorted list with projects
        :rtype: list

        """
        try:
            allProjects = self.structuredSessionObj.getProjects()
            for idx, entry in enumerate(allProjects): # the behaviour of list elements in python drives me crazy
                processes = self.structuredSessionObj.getProcesses(entry[ProjectDescription.projectID])
                allProjects[idx][ProjectOutput.processesCount] = len(processes) # no check needed since session is self contained
                allProjects[idx][ProjectOutput.processIDs] = list(processes.keys())
                # gather searchable data
                allProjects[idx][ProjectOutput.searchableData] = []
                # TODO
                
                if SessionContentSemperKI.processes in allProjects[idx]:
                    del allProjects[idx][SessionContentSemperKI.processes] # frontend doesn't need that
            
            return allProjects
        except (Exception) as error:
            logger.error(f"could not get all flat projects: {str(error)}")
            return error

    #######################################################
    def getProcessObj(self, projectID: str, processID: str) -> ProcessInterface:
        """
        Return the process and all its details

        :param projectID: The ID of the project (can be empty)
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :return: Process Object
        :rtype: ProcessInterface
        """
        try:
            if projectID == "":
                content = self.structuredSessionObj.getProcessPerID(processID)
            else:
                content = self.structuredSessionObj.getProcess(projectID, processID)
            returnObj = ProcessInterface(ProjectInterface(projectID, content[ProcessDescription.createdWhen], content[ProcessDescription.client]), processID, content[ProcessDescription.createdWhen], content[ProcessDescription.client])
            
            # dependencies are saved as list of processIDs 
            if ProcessDescription.dependenciesIn in content:
                dependenciesIn = content[ProcessDescription.dependenciesIn]
                dependenciesOut = content[ProcessDescription.dependenciesOut]
            else:
                dependenciesIn = []
                dependenciesOut = []
            
            returnObj.setValues(content[ProcessDescription.processDetails], content[ProcessDescription.processStatus], content[ProcessDescription.serviceDetails], content[ProcessDescription.serviceStatus], content[ProcessDescription.serviceType], content[ProcessDescription.client], content[ProcessDescription.files], content[ProcessDescription.messages], dependenciesIn, dependenciesOut, content[ProcessDescription.updatedWhen], content[ProcessDescription.accessedWhen])
            return returnObj
        except (Exception) as error:
            logger.error(f"Could not fetch process: {str(error)}")
            return error
        
    #######################################################
    def getProcess(self, projectID:str, processID:str):
        """
        Return the process and all its details as dict

        :param projectID: The ID of the project
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :return: Dictionary containing the process
        :rtype: dict

        """
        try:
            processObj = self.getProcessObj(projectID, processID)
            return processObj.toDict()

        except (Exception) as error:
            logger.error(f"Could not fetch process: {str(error)}")
            return error

    #######################################################
    def getProcessDependencies(self, projectID:str, processID:str) -> tuple[list[ProcessInterface],list[ProcessInterface]]:
        """
        Return the process dependencies 

        :param projectID: The ID of the project
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :return: Incoming and outgoing dependencies
        :rtype: tuple[list,list]

        """
        try:
            processObject = self.getProcessObj(projectID, processID)
            if isinstance(processObject, Exception):
                raise processObject
            dependenciesIn = []
            dependenciesOut = []
            for dependentProcessID in processObject.dependenciesIn.all():
                dependentProcess = self.getProcessObj(projectID, dependentProcessID)
                if isinstance(dependentProcess, Exception):
                    raise dependentProcess
                dependenciesIn.append(dependentProcess)
            for dependentProcessID in processObject.dependenciesOut.all():
                dependentProcess = self.getProcessObj(projectID, dependentProcessID)
                if isinstance(dependentProcess, Exception):
                    raise dependentProcess
                dependenciesOut.append(dependentProcess)

            return (dependenciesIn, dependenciesOut)

        except (Exception) as error:
            logger.error(f"Could not fetch dependencies: {str(error)}")
            return ([],[])
        

    #######################################################
    def createProcess(self, projectID:str, processID:str, client:str):
        """
        Create the process

        :param projectID: The ID of the project
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :param client: anonymous client, necessary for interface
        :type client: str
        :return: Nothing
        :rtype: None
        
        """

        now = timezone.now()

        self.structuredSessionObj.setProcess(projectID, processID, ProcessInterface(ProjectInterface(projectID, str(now), client), processID, str(now), client).toDict())

    ###################################################
    def deleteProcess(self, processID:str, processObj=None):
        """
        Delete specific process.

        :param processID: unique process ID to be deleted
        :type processID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        try:
            currentProcess = self.structuredSessionObj.getProcessPerID(processID)
            files = currentProcess[ProcessDescription.files]
            for fileKey in files:
                fileObj = files[fileKey]
                if FileObjectContent.isFile not in fileObj or fileObj[FileObjectContent.isFile]:
                    if fileObj[FileObjectContent.remote]:
                        s3.manageRemoteS3.deleteFile(fileObj[FileObjectContent.path])
                    else:
                        s3.manageLocalS3.deleteFile(fileObj[FileObjectContent.path])
            self.structuredSessionObj.deleteProcess(processID)

        except (Exception) as error:
            logger.error(f'could not delete project: {str(error)}')
            return error

    ##############################################
    def updateProcess(self, projectID:str, processID:str, updateType: ProcessUpdates, content:dict, updatedBy:str) -> tuple[str,dict]|Exception:
        """
        Change details of a process like its status, or save communication. 

        :param projectID: Project that this process belongs to
        :type projectID: str
        :param processID: unique processID to be edited
        :type processID: str
        :param updateType: changed process details
        :type updateType: EnumUpdates
        :param content: changed process, can be many stuff
        :type content: json dict
        :param updatedBy: ID of the person who updated the process (for history)
        :type updatedBy: str
        :return: The relevant thing that got updated, for event queue
        :rtype: tuple[str,dict]|Exception

        """
        try:
            outContent = ""
            outAdditionalInformation = {}
            updated = timezone.now()
            currentProcess = self.structuredSessionObj.getProcess(projectID, processID)
            dataID = crypto.generateURLFriendlyRandomString()
            
            if updateType == ProcessUpdates.messages:
                if MessageInterfaceFromFrontend.origin in content:
                    origin = content[MessageInterfaceFromFrontend.origin]
                    if origin in currentProcess[ProcessDescription.messages]:
                        currentProcess[ProcessDescription.messages][origin].append(content)
                    else:
                        currentProcess[ProcessDescription.messages][origin] = [content]
                else:
                    if MessageInterfaceFromFrontend.messages in currentProcess[ProcessDescription.messages]:
                        currentProcess[ProcessDescription.messages][MessageInterfaceFromFrontend.messages].append(content)
                    else:
                        currentProcess[ProcessDescription.messages][MessageInterfaceFromFrontend.messages] = [content]
                    self.createDataEntry(content, dataID, processID, DataType.MESSAGE, updatedBy)
                outContent = content[MessageInterfaceFromFrontend.text]

            elif updateType == ProcessUpdates.files:
                for entry in content:
                    currentProcess[ProcessDescription.files][content[entry][FileObjectContent.id]] = content[entry]
                    self.createDataEntry(content[entry], dataID, processID, DataType.FILE, updatedBy, {}, content[entry][FileObjectContent.id])
                    outContent += content[entry][FileObjectContent.fileName] + ","
                outContent = outContent.rstrip(",")

            elif updateType == ProcessUpdates.serviceType:
                currentProcess[ProcessDescription.serviceType] = content
                currentProcess[ProcessDescription.serviceDetails] = serviceManager.getService(content).initializeServiceDetails(currentProcess[ProcessDescription.serviceDetails])
                self.createDataEntry(content, dataID, processID, DataType.SERVICE, updatedBy, {ProcessUpdates.serviceType: content})
                outContent = content
            
            elif updateType == ProcessUpdates.serviceDetails:
                serviceType = currentProcess[ProcessDescription.serviceType]
                if serviceType != serviceManager.getNone():
                    currentProcess[ProcessDescription.serviceDetails] = serviceManager.getService(serviceType).updateServiceDetails(currentProcess[ProcessDescription.serviceDetails], content)
                    self.createDataEntry(content, dataID, processID, DataType.SERVICE, updatedBy, {ProcessUpdates.serviceDetails: content})
                    for entry in content:
                        outContent += entry + ","
                    outContent = outContent.rstrip(",")
                else:
                    raise Exception("No Service chosen!")
            
            elif updateType == ProcessUpdates.serviceStatus:
                currentProcess[ProcessDescription.serviceStatus] = content
                self.createDataEntry(content, dataID, processID, DataType.SERVICE, updatedBy, {ProcessUpdates.serviceStatus: content})
                outContent = str(content)

            elif updateType == ProcessUpdates.processDetails:
                for entry in content:
                    if entry == ProcessDetails.priorities:
                        if ProcessDetails.priorities in currentProcess[ProcessDescription.processDetails]:
                            # update only one priority, the for loop is a shortcut to getting the key/priority
                            for prio in content[entry]:
                                currentProcess[ProcessDescription.processDetails][ProcessDetails.priorities][prio][PriorityTargetsSemperKI.value] = content[entry][prio][PriorityTargetsSemperKI.value]
                                self.createDataEntry(content, dataID, processID, DataType.DETAILS, updatedBy)
                        else:
                            currentProcess[ProcessDescription.processDetails][ProcessDetails.priorities] = content[entry]
                            self.createDataEntry(content, dataID, processID, DataType.DETAILS, updatedBy)# is set during creation and therefore complete
                    else:
                        currentProcess[ProcessDescription.processDetails][entry] = content[entry]
                        self.createDataEntry(content, dataID, processID, DataType.DETAILS, updatedBy)
                    outContent += entry + ","
                outContent = outContent.rstrip(",")

            elif updateType == ProcessUpdates.processStatus:
                currentProcess[ProcessDescription.processStatus] = content
                self.createDataEntry(content, dataID, processID, DataType.STATUS, updatedBy)
                outContent = str(content)

            elif updateType == ProcessUpdates.provisionalContractor:
                currentProcess[ProcessDescription.processDetails][ProcessDetails.provisionalContractor] = content
                self.createDataEntry(content, dataID, processID, DataType.OTHER, updatedBy, {ProcessUpdates.provisionalContractor: content})
                outContent = content

            elif updateType in [ProcessUpdates.dependenciesIn, ProcessUpdates.dependenciesOut]:
                dependencyKey = ProcessDescription.dependenciesIn if updateType == ProcessUpdates.dependenciesIn else ProcessDescription.dependenciesOut
                oppositeKey = ProcessDescription.dependenciesOut if updateType == ProcessUpdates.dependenciesIn else ProcessDescription.dependenciesIn
                assert isinstance(content, list), "DependencyIn Content is not a list"
                for contentProcessID in content:
                    if contentProcessID not in currentProcess.setdefault(dependencyKey, []):
                        currentProcess[dependencyKey].append(contentProcessID)
                
                    dependentProcess = self.structuredSessionObj.getProcess(projectID, contentProcessID)
                    if processID not in dependentProcess.setdefault(oppositeKey, []):
                        dependentProcess[oppositeKey].append(processID)
                self.createDataEntry(content, dataID, processID, DataType.DEPENDENCY, updatedBy, {updateType: content})
                outContent = content

            elif updateType == ProcessUpdates.additionalInput:
                currentProcess[ProcessDescription.processDetails][ProcessDetails.additionalInput] = content
                self.createDataEntry(content, dataID, processID, DataType.OTHER, updatedBy, {ProcessUpdates.additionalInput: content})
                outContent = content
            else:
                raise Exception(f"updateProcess {updateType} not implemented")
            
            currentProcess[ProcessDescription.updatedWhen] = str(updated)
            self.structuredSessionObj.setProcess(projectID, processID, currentProcess)
            
            return (outContent, outAdditionalInformation)
        except (Exception) as error:
            logger.error(f"could not update process: {str(error)}")
            return error
        
    ##############################################
    def deleteFromProcess(self, projectID:str, processID:str, updateType: ProcessUpdates, content:dict, deletedBy:str):
        """
        Delete details of a process like its status, or content. 

        :param projectID: Project that this process belongs to
        :type projectID: str
        :param processID: unique process ID to be edited
        :type processID: str
        :param updateType: changed process details
        :type updateType: EnumUpdates
        :param content: deletions
        :type content: json dict
        :param deletedBy: ID of the person who deleted from the process (for history)
        :type deletedBy: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        try:
            updated = timezone.now()
            currentProcess = self.structuredSessionObj.getProcess(projectID, processID)
            dataID = crypto.generateURLFriendlyRandomString()

            if updateType == ProcessUpdates.messages:
                origin = content['origin']
                currentProcess[ProcessDescription.messages][MessageInterfaceFromFrontend[origin]] = []
                self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.MESSAGE, "content": content})

            elif updateType == ProcessUpdates.files:
                for entry in content:
                    if FileObjectContent.isFile not in currentProcess[ProcessDescription.files][entry] or currentProcess[ProcessDescription.files][entry][FileObjectContent.isFile]:
                        if currentProcess[ProcessDescription.files][entry][FileObjectContent.remote]:
                            s3.manageRemoteS3.deleteFile(currentProcess[ProcessDescription.files][entry][FileObjectContent.path])
                        else:
                            s3.manageLocalS3.deleteFile(currentProcess[ProcessDescription.files][entry][FileObjectContent.path])
                    del currentProcess[ProcessDescription.files][entry]
                    self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.FILE, "content": entry})

            elif updateType == ProcessUpdates.serviceType:
                if currentProcess[ProcessDescription.serviceType] != serviceManager.getNone():
                    serviceType = currentProcess[ProcessDescription.serviceType]
                    currentProcess[ProcessDescription.serviceDetails] = serviceManager.getService(serviceType).deleteServiceDetails(currentProcess[ProcessDescription.serviceDetails], currentProcess[ProcessDescription.serviceDetails])
                currentProcess[ProcessDescription.serviceStatus] = 0
                if ProcessDetails.additionalInput in currentProcess[ProcessDescription.processDetails]:
                    currentProcess[ProcessDescription.processDetails][ProcessDetails.additionalInput] = {}
                currentProcess[ProcessDescription.serviceType] = serviceManager.getNone()
                self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.SERVICE, "content": ProcessUpdates.serviceType})

            elif updateType == ProcessUpdates.serviceDetails:
                serviceType = currentProcess[ProcessDescription.serviceType]
                if serviceType != serviceManager.getNone():
                    currentProcess[ProcessDescription.serviceDetails] = serviceManager.getService(serviceType).deleteServiceDetails(currentProcess[ProcessDescription.serviceDetails], content)
                    self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.SERVICE, "content": ProcessUpdates.serviceDetails})
                else:
                    raise Exception("No Service chosen!")

            elif updateType == ProcessUpdates.serviceStatus:
                currentProcess[ProcessDescription.serviceStatus] = 0
                self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.SERVICE, "content": ProcessUpdates.serviceStatus})

            elif updateType == ProcessUpdates.processDetails:
                for entry in content:
                    del currentProcess[ProcessDescription.processDetails][entry]
                self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.DETAILS, "content": ProcessUpdates.processDetails})

            elif updateType == ProcessUpdates.processStatus:
                currentProcess[ProcessDescription.processStatus] = StateDescriptions.processStatusAsInt(StateDescriptions.ProcessStatusAsString.DRAFT)
                self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.STATUS, "content": ProcessUpdates.processStatus})

            elif updateType == ProcessUpdates.provisionalContractor:
                currentProcess[ProcessDescription.processDetails][ProcessUpdates.provisionalContractor] = {}
                self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.OTHER, "content": ProcessUpdates.provisionalContractor})

            elif updateType in [ProcessUpdates.dependenciesIn, ProcessUpdates.dependenciesOut]:
                dependencyKey = ProcessDescription.dependenciesIn if updateType == ProcessUpdates.dependenciesIn else ProcessDescription.dependenciesOut
                oppositeKey = ProcessDescription.dependenciesOut if updateType == ProcessUpdates.dependenciesIn else ProcessDescription.dependenciesIn
                assert isinstance(content, list), "DependencyOut Content is not a list"
                for contentProcessID in content:
                    if contentProcessID in currentProcess.get(dependencyKey, []):
                        currentProcess[dependencyKey].remove(contentProcessID)
                    dependentProcess = self.structuredSessionObj.getProcess(projectID, contentProcessID)
                    if contentProcessID in dependentProcess.get(oppositeKey, []):
                        dependentProcess[oppositeKey].remove(processID)
                self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.DEPENDENCY, "content": updateType})

            elif updateType == ProcessUpdates.additionalInput:
                currentProcess[ProcessDescription.processDetails][ProcessDetails.additionalInput] = {}
                self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.OTHER, "content": ProcessUpdates.additionalInput})

            else:
                raise Exception(f"deleteFromProcess {updateType} not implemented")

            currentProcess[ProcessDescription.updatedWhen] = str(updated)
            self.structuredSessionObj.setProcess(projectID, processID, currentProcess)

            return True
        except (Exception) as error:
            logger.error(f"could not delete from process: {str(error)}")
            return error
        
    
    ##############################################
    def getProcessesPerPID(self, projectID):
        """
        Retrieve infos about one project, for admins

        :param projectID: project of interest
        :type projectID: str
        :return: list of all processes of that project
        :rtype: list
        """
        processes = self.structuredSessionObj.getProcesses(projectID)
        return list(processes.values())
    
    ##############################################
    def checkIfFilesAreRemote(self, projectID:str, processID:str) -> bool:
        """
        If at least one file is remote, say so to trigger upload to remote for new files as well

        :param projectID: The ID of the project that the process is part of
        :type projectID: str
        :param processID: The ID of the process in question
        :type processID: str
        :return: True if remote, false if local
        :rtype: bool
        
        """
        try:
            processObj = self.structuredSessionObj.getProcess(projectID, processID)
            for fileKey in processObj[ProcessDescription.files]:
                if processObj[ProcessDescription.files][fileKey][FileObjectContent.remote]:
                    return True
                
            return False
        except (Exception) as error:
            logger.error(f'could not check if files are remote: {str(error)}')
            return False
    
    ##################################################
    def createDataEntry(self, data, dataID, processID, typeOfData:DataType, createdBy:str, details={}, IDofData=""):
        """
        Create an entry in the Data history

        :param data: The data itself
        :type data: Dict in JSON
        :param dataID: The ID of that date
        :type dataID: Str
        :param processID: process it belongs to
        :type processID: str
        :param typeOfData: The type of this data
        :type typeOfData: DataType
        :param createdBy: Who created it (hashed ID)
        :type createdBy: Str
        :param details: Some metadata
        :type details: JSON Dict
        :param IDofData: If the data has an id, save it
        :type IDofData: Str
        :return: Nothing
        :rtype: None
        """
        try:
            if 'data_history' not in self.structuredSessionObj.currentSession:
                self.structuredSessionObj.currentSession['data_history'] = []
            
            dataEntry = DataInterface(dataID, processID, typeOfData, data, details, createdBy, IDofData, str(timezone.now()))
            
            self.structuredSessionObj.currentSession['data_history'].append(dataEntry.toDict())
            self.structuredSessionObj.currentSession.modified = True

        except Exception as error:
            logger.error(f'could not create data entry: {str(error)}')
        
        return None
    
    ##################################################
    def deleteAllDataEntriesOfProcess(self, processID:str) -> None:
        """
        Delete all entries in history of the process from session
        
        """
        try:
            newList = []
            if 'data_history' in self.structuredSessionObj.currentSession:
                for entry in self.structuredSessionObj.currentSession['data_history']:
                    if entry[DataDescription.processID] != processID:
                        newList.append(entry)
                if len(newList) == 0:
                    del self.structuredSessionObj.currentSession['data_history']
                else:
                    self.structuredSessionObj.currentSession['data_history'] = newList
                
        except (Exception) as error:
            logger.error(f'could not delete data entries: {str(error)}')

