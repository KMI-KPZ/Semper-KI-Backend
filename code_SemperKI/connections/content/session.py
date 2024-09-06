"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Offers an interface to access the session dictionary in a structured way
"""

from django.utils import timezone
import logging, copy

from Generic_Backend.code_General.definitions import SessionContent, FileObjectContent
from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.connections.postgresql.pgProfiles import profileManagement

from ...definitions import SessionContentSemperKI, MessageInterfaceFromFrontend
from ...definitions import ProjectUpdates, ProcessUpdates, ProcessDetails
from ...definitions import *
from Generic_Backend.code_General.definitions import FileObjectContent, SessionContent
from ...modelFiles.processModel import ProcessInterface, ProcessDescription
from ...modelFiles.projectModel import ProjectInterface, ProjectDescription
from ...serviceManager import serviceManager
import code_SemperKI.states.stateDescriptions as StateDescriptions
from .abstractInterface import AbstractContentInterface
from Generic_Backend.code_General.utilities import crypto

logger = logging.getLogger("errors")
# TODO: history alias Data

#######################################################
class StructuredSession():
    """
    Interface class that handles the session content

    """

    # currentSession : dict = {}

    # #######################################################
    def __init__(self, session):
        self.currentSession = session
        if SessionContentSemperKI.CURRENT_PROJECTS not in self.currentSession:
            self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS] = {}
    
    #######################################################
    def _get_nested(self, keys, default=None):
        current = self.currentSession
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    ################################################################
    def _set_nested(self, keys, value):
        """Helper method to safely set nested dictionary values"""
        current = self.currentSession
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value
        
    ################################################################    
    def getSession(self):
        """
        Return current session
        
        """
        return self.currentSession
    
    #######################################################
    def save_session(self):
        if hasattr(self.currentSession, 'save'):
            self.currentSession.save()
        logger.debug("Session saved")
    
    #######################################################
    def getIfContentIsInSession(self) -> bool:
        """
        Tell whether there is content in the session

        :return: if there are projects in the session, use these and tell the this
        :rtype: bool
        
        """

        return SessionContentSemperKI.CURRENT_PROJECTS in self.currentSession

    #######################################################
    def clearContentFromSession(self) -> None:
        """
        Delete all projects from session

        :return: Nothing
        :rtype: None
        
        """
        if SessionContentSemperKI.CURRENT_PROJECTS in self.currentSession:
            del self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS]
        self.currentSession.modified = True

    #######################################################
    def getProject(self, projectID: str) -> dict:
        """
        Return specific project from session

        :param projectID: The ID of the project
        :type projectID: str
        :return: Dictionary with project in it
        :rtype: dict
        """
        logger.debug(f"Current session structure: {self.currentSession}")
        logger.debug(f"Attempting to get project with ID: {projectID}")
        if SessionContentSemperKI.CURRENT_PROJECTS not in self.currentSession:
            logger.warning(f"No projects found in session")
            return {}
        if projectID not in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS]:
            logger.warning(f"Project with ID {projectID} not found in session")
            return {}
        project = self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]
        logger.debug(f"Retrieved project: {project}")
        return project

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
        self.save_session()

    #######################################################
    def deleteProject(self, projectID:str):
        """
        Delete the project

        :param projectID: The ID of the project
        :type projectID: str
        :return: Nothing
        :rtype: None
        """

        # if projectID in self._get_nested([SessionContentSemperKI.CURRENT_PROJECTS], {}):
        #     del self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]
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
        # return self._get_nested([SessionContentSemperKI.CURRENT_PROJECTS, projectID, SessionContentSemperKI.processes], {})
        return self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes]
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
        # return self._get_nested([SessionContentSemperKI.CURRENT_PROJECTS, projectID, SessionContentSemperKI.processes, processID], {})
        return self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID]
        
    #######################################################
    def getProcessPerID(self, processID:str):
        """
        Get process without project ID

        :param processID: The ID of the process
        :type processID: str
        :return: Dictionary with process in it
        :rtype: dict
        
        """
        for projectID, project in self._get_nested([SessionContentSemperKI.CURRENT_PROJECTS], {}).items():
            if processID in project.get(SessionContentSemperKI.processes, {}):
                return project[SessionContentSemperKI.processes][processID]
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
        for projectID, project in self._get_nested([SessionContentSemperKI.CURRENT_PROJECTS], {}).items():
            if processID in project.get(SessionContentSemperKI.processes, {}):
                return (projectID, project[SessionContentSemperKI.processes][processID])
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
        self._set_nested([SessionContentSemperKI.CURRENT_PROJECTS, projectID, SessionContentSemperKI.processes, processID], content)

    #######################################################
    def deleteProcess(self, projectID, processID):
        """
        Delete one specific process

        :param processID: The ID of the process
        :type processID: str
        :return: Nothing
        :rtype: None
        
        """
        processes = self._get_nested([SessionContentSemperKI.CURRENT_PROJECTS, projectID, SessionContentSemperKI.processes], {})
        if processID in processes:
            del processes[processID]

#######################################################
class ProcessManagementSession(AbstractContentInterface):
    """
    Offers an interface equal to that of the postgres, albeit session based
    
    """

    #######################################################
    def __init__(self, session):
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
        session = self.structuredSessionObj.getSession()
        
        profile_class = session.get(SessionContent.PG_PROFILE_CLASS)
        if profile_class and profile_class in profileManagement:
            return profileManagement[profile_class].getClientID(session)
        else:
            logger.error(f"Invalid profile class in session: {profile_class}")
            return ""
        
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
            return project.get(ProjectDescription.client) == userHashID
        if processID:
            projectID, process = self.structuredSessionObj.getProcessAndProjectPerID(processID)
            return process.get(ProcessDescription.client) == userHashID
        return False    
    
    #######################################################
    def getData(self, processID):
        """
        Get all data entries for a process

        :param processID: The ID of the process
        :type processID: str
        :return: List of data entries
        :rtype: list
        """
        process = self.structuredSessionObj.getProcessPerID(processID)
        return process.get(ProcessDescription.data, [])
    
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
        data = self.getData(processID)
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
        data = self.getData(processID)
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
        data = self.getData(processID)
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
        except Exception as error:
            logger.error(f"Could not get project object: {str(error)}")
            return None

    #######################################################
    def createProject(self, projectID:str, client:str):
        now = timezone.now()
        project_dict = ProjectInterface(projectID, str(now), client).toDict()
        self.structuredSessionObj.setProject(projectID, project_dict)
        logger.debug(f"Created project: {project_dict}")
        # Verify the project was added correctly
        # saved_project = self.structuredSessionObj.getProject(projectID)
        # logger.debug(f"Verified saved project: {saved_project}")

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
            logger.debug(f"Attempting to get project with ID: {projectID}")
            savedProject = self.structuredSessionObj.getProject(projectID)
            if not savedProject:
                logger.warning(f"Project with ID {projectID} not found or empty")
                return {}
            
            savedProject = copy.deepcopy(savedProject)
            logger.debug(f"Retrieved project before processing: {savedProject}")
            
            if SessionContentSemperKI.processes in savedProject:
                savedProject[SessionContentSemperKI.processes] = list(savedProject[SessionContentSemperKI.processes].values())
            else:
                savedProject[SessionContentSemperKI.processes] = []
            
            logger.debug(f"Processed project: {savedProject}")
            return savedProject
        except Exception as error:
            logger.error(f'Could not get project: {str(error)}', exc_info=True)
            return {}

    ##############################################
    def getProjectForContractor(self, projectID, contractorHashID):
        """
        Get info about one project for an organization as a contractor.

        :param projectID: ID of the project
        :type projectID: str
        :param contractorHashID: The ID of the contractor
        :type contractorHashID: str
        :return: dict with info about that project
        :rtype: dict
        """
        try:
            projectObj = self.structuredSessionObj.getProject(projectID)
            output = projectObj.copy()
            processesOfThatProject = []
            for entry in projectObj.get(SessionContentSemperKI.processes, {}).values():
                if entry.get(ProcessDescription.contractor) == contractorHashID:
                    processesOfThatProject.append(entry)
            output[SessionContentSemperKI.processes] = processesOfThatProject
            return output
        except Exception as error:
            logger.error(f'could not get project for contractor: {str(error)}')
            return {}
        
        ####################################################################################
    def getAllUsersOfProject(self, projectID):
        """
        Get all user IDs that are connected to that project.

        :param projectID: unique project ID
        :type projectID: str
        :return: Set of all user IDs
        :rtype: Set
        """
        try:
            currentProject = self.structuredSessionObj.getProject(projectID)
            users = set()
            
            # Assuming client ID is stored directly in the project
            clientID = currentProject.get(ProjectDescription.client)
            
            if clientID:
                users.add(clientID)
                
                # If we need to handle organizations, we would need to store this information in the session
                # This is a placeholder for how we might handle it:
                if SessionContentSemperKI.ORGANIZATIONS in self.structuredSessionObj.getSession():
                    org = self.structuredSessionObj.getSession()[SessionContentSemperKI.ORGANIZATIONS].get(clientID)
                    if org:
                        users.update(org.get('users', []))
            
            return users
        except Exception as error:
            logger.error(f'could not get all users of project: {str(error)}')
        return set()
        #############################################################################
    def updateProject(self, projectID:str, updateType: ProjectUpdates, content:dict):
        """
        Change details of a project like its status.

        :param projectID: project ID that this project belongs to
        :type projectID: str
        :param updateType: changed project details
        :type updateType: ProjectUpdates
        :param content: changed project, can be many stuff
        :type content: json dict
        :return: Flag if it worked or not
        :rtype: Bool
        """
        updated = timezone.now()
        try:
            # currentProject = self.structuredSessionObj.getProject(projectID)
            # if not currentProject:
            #     logger.error(f"Project with ID {projectID} not found")
            #     return False

            if updateType == ProjectUpdates.projectStatus:
                currentProject = self.structuredSessionObj.getProject(projectID)
                currentProject[ProjectDescription.projectStatus] = content
            elif updateType == ProjectUpdates.projectDetails:
                currentProject = self.structuredSessionObj.getProject(projectID)
                if ProjectDescription.projectDetails not in currentProject:
                    currentProject[ProjectDescription.projectDetails] = {}
                currentProject[ProjectDescription.projectDetails].update(content)
                currentProject[ProjectDescription.updatedWhen] = str(updated)
            else:
                raise ValueError(f"updateProject {updateType} not implemented")

             ######shift this line in updatetype details
            self.structuredSessionObj.setProject(projectID, currentProject)
            return True
        except Exception as error:
            logger.error(f'Could not update project: {str(error)}')
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
            for idx, entry in enumerate(allProjects):
                allProjects[idx]["processesCount"] = len(self.structuredSessionObj.getProcesses(entry[ProjectDescription.projectID]))
                if SessionContentSemperKI.processes in allProjects[idx]:
                    del allProjects[idx][SessionContentSemperKI.processes]
            
            return allProjects
        except Exception as error:
            logger.error(f"could not get all flat projects: {str(error)}")
            return error

    #######################################################
    def verifyProcess(self, processID, session, userID):
        """
        Verify the process.

        :param processID: The ID of the process
        :type processID: str
        :param session: Session of this user
        :type session: dict
        :param userID: The ID of the user verifying the process
        :type userID: str
        :return: None or Error
        :rtype: None or Exception
        """
        try:
            dataID = crypto.generateURLFriendlyRandomString()
            self.createDataEntry("Verification started", dataID, processID, DataType.STATUS, userID)
            # In a session-based approach, we might need to handle verification differently
            # For now, we'll just update the process status
            projectID, process = self.structuredSessionObj.getProcessAndProjectPerID(processID)
            process[ProcessDescription.processStatus] = StateDescriptions.processStatusAsInt(StateDescriptions.ProcessStatusAsString.VERIFICATION_COMPLETED)
            self.structuredSessionObj.setProcess(projectID, processID, process)
            return None
        except Exception as error:
            logger.error(f"verifyProcess: {str(error)}")
            return error
        
    #######################################################################
    def sendProcess(self, processID, session, userID):
        """
        Send the process to its contractor(s).

        :param processID: The ID of the process
        :type processID: str
        :param session: Who ordered the sendaway
        :type session: dict
        :param userID: Who ordered the sendaway
        :type userID: str
        :return: None or Error
        :rtype: None or Exception
        """
        try:
            projectID, process = self.structuredSessionObj.getProcessAndProjectPerID(processID)
            if process[ProcessDescription.processStatus] < StateDescriptions.processStatusAsInt(StateDescriptions.ProcessStatusAsString.VERIFICATION_COMPLETED):
                raise Exception("Not verified yet!")

            contractorID = process[ProcessDescription.processDetails].get(ProcessDetails.provisionalContractor)
            if not contractorID:
                raise Exception("No provisional contractor set!")

            dataID = crypto.generateURLFriendlyRandomString()
            self.createDataEntry({"Action": "SendToContractor", "ID": contractorID}, dataID, processID, DataType.OTHER, userID, {})

            # Update process status
            process[ProcessDescription.processStatus] = StateDescriptions.processStatusAsInt(StateDescriptions.ProcessStatusAsString.SENT_TO_CONTRACTOR)
            self.structuredSessionObj.setProcess(projectID, processID, process)

            # In a session-based approach, we might need to handle file transfer differently
            # For now, we'll just update the file status
            for fileKey in process.get(ProcessDescription.files, {}):
                process[ProcessDescription.files][fileKey][FileObjectContent.remote] = True

            self.structuredSessionObj.setProcess(projectID, processID, process)

            # TODO: Implement email sending logic
            return None
        except Exception as error:
            logger.error(f"sendProcess: {str(error)}")
            return error
        
    #############################################################################
    def getProcessObj(self, projectID: str, processID: str) ->ProcessInterface:
        """
        Return the process and all its details

        :param projectID: The ID of the project
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :return: Process Object or Exception if an error occurs
        :rtype: Union[ProcessInterface, Exception]
        """
        try:
            content = self.structuredSessionObj.getProcess(projectID, processID)
            if not content:
                logger.warning(f"Process not found (projectID: {projectID}, processID: {processID})")
                return None

            returnObj = ProcessInterface(
                ProjectInterface(projectID, content[ProcessDescription.createdWhen], content[ProcessDescription.client]),
                processID,
                content[ProcessDescription.createdWhen],
                content[ProcessDescription.client]
            )
            
            # dependencies are saved as list of processIDs 
            dependenciesIn = content.get(ProcessDescription.dependenciesIn, [])
            dependenciesOut = content.get(ProcessDescription.dependenciesOut, [])
            
            returnObj.setValues(
                content.get(ProcessDescription.processDetails, {}),
                content.get(ProcessDescription.processStatus),
                content.get(ProcessDescription.serviceDetails, {}),
                content.get(ProcessDescription.serviceStatus),
                content.get(ProcessDescription.serviceType),
                content.get(ProcessDescription.client),
                content.get(ProcessDescription.files, {}),
                content.get(ProcessDescription.messages, {}),
                dependenciesIn,
                dependenciesOut,
                content.get(ProcessDescription.updatedWhen),
                content.get(ProcessDescription.accessedWhen)
            )
            return returnObj
        except Exception as error:
            logger.error(f"Could not fetch process (projectID: {projectID}, processID: {processID}): {str(error)}")
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
            return self._get_nested([SessionContentSemperKI.CURRENT_PROJECTS, projectID, SessionContentSemperKI.processes, processID], {})
        except Exception as error:
            logger.error(f"Error fetching process (projectID: {projectID}, processID: {processID}): {str(error)}")
            return {}

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
            processObject = self.structuredSessionObj.getProcess(projectID, processID)
            dependenciesIn = [self.structuredSessionObj.getProcess(projectID, depID) for depID in processObject.get(ProcessDescription.dependenciesIn, [])]
            dependenciesOut = [self.structuredSessionObj.getProcess(projectID, depID) for depID in processObject.get(ProcessDescription.dependenciesOut, [])]
            return (dependenciesIn, dependenciesOut)
        except Exception as error:
            logger.error(f"Could not fetch dependencies: {str(error)}")
            return ([], [])
        

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
        processInterface = ProcessInterface(ProjectInterface(projectID, str(now), client), processID, str(now), client)
        self.structuredSessionObj.setProcess(projectID, processID, processInterface.toDict())
        
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
            projectID, currentProcess = self.structuredSessionObj.getProcessAndProjectPerID(processID)
            files = currentProcess.get(ProcessDescription.files, {})
            for fileKey, fileObj in files.items():
                if fileObj[FileObjectContent.remote]:
                    s3.manageRemoteS3.deleteFile(fileObj[FileObjectContent.path])
                else:
                    s3.manageLocalS3.deleteFile(fileObj[FileObjectContent.path])
            self.structuredSessionObj.deleteProcess(projectID, processID)
            return True
        except Exception as error:
            logger.error(f'could not delete process: {str(error)}')
            return error

    ##############################################
    def updateProcess(self, projectID:str, processID:str, updateType: ProcessUpdates, content:dict, updatedBy:str):
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
        :return: Flag if it worked or not
        :rtype: Bool

        """
        try:
            updated = timezone.now()
            currentProcess = self.structuredSessionObj.getProcess(projectID, processID)
            dataID = crypto.generateURLFriendlyRandomString()
            
            if updateType == ProcessUpdates.messages:
                if 'origin' in content:
                    origin = content['origin']
                    if origin not in currentProcess.get(ProcessDescription.messages, {}):
                        currentProcess.setdefault(ProcessDescription.messages, {})[origin] = []
                    currentProcess[ProcessDescription.messages][origin].append(content)
                else:
                    currentProcess.setdefault(ProcessDescription.messages, {}).setdefault(MessageInterfaceFromFrontend.messages, []).append(content)
                self.createDataEntry(content, dataID, processID, DataType.MESSAGE, updatedBy)
                
            elif updateType == ProcessUpdates.files:
                for entry in content:
                    currentProcess.setdefault(ProcessDescription.files, {})[content[entry][FileObjectContent.id]] = content[entry]
                    self.createDataEntry(content[entry], dataID, processID, DataType.FILE, updatedBy, {}, content[entry][FileObjectContent.id])

            elif updateType == ProcessUpdates.serviceDetails:
                serviceType = currentProcess.get(ProcessDescription.serviceType)
                if serviceType != serviceManager.getNone():
                    currentProcess[ProcessDescription.serviceDetails] = serviceManager.getService(serviceType).updateServiceDetails(
                        currentProcess.get(ProcessDescription.serviceDetails, {}), content
                    )
                    self.createDataEntry(content, dataID, processID, DataType.SERVICE, updatedBy, {ProcessUpdates.serviceDetails: ""})
                else:
                    raise Exception("No Service chosen!")
                
            elif updateType == ProcessUpdates.serviceStatus:
                currentProcess[ProcessDescription.serviceStatus] = content
                self.createDataEntry(content, dataID, processID, DataType.SERVICE, updatedBy, {ProcessUpdates.serviceStatus: ""})
                
            elif updateType == ProcessUpdates.processDetails:
                currentProcess.setdefault(ProcessDescription.processDetails, {}).update(content)
                self.createDataEntry(content, dataID, processID, DataType.DETAILS, updatedBy)

            elif updateType == ProcessUpdates.processStatus:
                currentProcess[ProcessDescription.processStatus] = content
                self.createDataEntry(content, dataID, processID, DataType.STATUS, updatedBy)
            
            elif updateType == ProcessUpdates.provisionalContractor:
                currentProcess.setdefault(ProcessDescription.processDetails, {})[ProcessDetails.provisionalContractor] = content
                self.createDataEntry(content, dataID, processID, DataType.OTHER, updatedBy, {ProcessUpdates.provisionalContractor: ""})
                                
            elif updateType in [ProcessUpdates.dependenciesIn, ProcessUpdates.dependenciesOut]:
                dependency_key = ProcessDescription.dependenciesIn if updateType == ProcessUpdates.dependenciesIn else ProcessDescription.dependenciesOut
                opposite_key = ProcessDescription.dependenciesOut if updateType == ProcessUpdates.dependenciesIn else ProcessDescription.dependenciesIn
                
                if content not in currentProcess.setdefault(dependency_key, []):
                    currentProcess[dependency_key].append(content)
                
                dependentProcess = self.structuredSessionObj.getProcess(projectID, content)
                if processID not in dependentProcess.setdefault(opposite_key, []):
                    dependentProcess[opposite_key].append(processID)
                self.createDataEntry(content, dataID, processID, DataType.DEPENDENCY, updatedBy, {updateType: content})
            else:
                raise Exception(f"updateProcess {updateType} not implemented")
            
            currentProcess[ProcessDescription.updatedWhen] = str(updated)
            self.structuredSessionObj.setProcess(projectID, processID, currentProcess)
            
            return True
        except Exception as error:
            logger.error(f"could not update process: {str(error)}")
            return error
        
    ##############################################
    def deleteFromProcess(self, projectID:str, processID:str, updateType: ProcessUpdates, content:dict, deletedBy:str):
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
                    if currentProcess[ProcessDescription.files][entry][FileObjectContent.remote]:
                        s3.manageRemoteS3.deleteFile(currentProcess[ProcessDescription.files][entry][FileObjectContent.path])
                    else:
                        s3.manageLocalS3.deleteFile(currentProcess[ProcessDescription.files][entry][FileObjectContent.path])
                    del currentProcess[ProcessDescription.files][entry]
                    self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.FILE, "content": entry})

            elif updateType == ProcessUpdates.serviceType:
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
                del currentProcess[ProcessDescription.processDetails][ProcessUpdates.provisionalContractor]
                self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.OTHER, "content": ProcessUpdates.provisionalContractor})

            elif updateType in [ProcessUpdates.dependenciesIn, ProcessUpdates.dependenciesOut]:
                dependency_key = ProcessDescription.dependenciesIn if updateType == ProcessUpdates.dependenciesIn else ProcessDescription.dependenciesOut
                if content in currentProcess.get(dependency_key, []):
                    currentProcess[dependency_key].remove(content)
                self.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.DEPENDENCY, "content": updateType})

            else:
                raise Exception(f"deleteFromProcess {updateType} not implemented")

            currentProcess[ProcessDescription.updatedWhen] = str(updated)
            self.structuredSessionObj.setProcess(projectID, processID, currentProcess)

            return True
        except Exception as error:
            logger.error(f"could not delete from process: {str(error)}")
            return error
        
    ##############################################
    def getInfoAboutProjectForWebsocket(self, projectID, processID, event, notification, clientOnly):
        """
        Retrieve information about the users connected to the project from the session.

        :param projectID: project ID to retrieve data from
        :type projectID: str
        :param processID: The process ID affected
        :type processID: str
        :param event: the event that happens
        :type event: str
        :param notification: The notification that wants to be sent
        :type notification: str
        :param clientOnly: Whether to include only the client or also the contractor
        :type clientOnly: bool
        :return: Dictionary of users with project ID and processes for the websocket to fire events
        :rtype: dict
        """
        dictForEventsAsOutput = {}
        process = self.structuredSessionObj.getProcess(projectID, processID)
        clientID = process.get(ProcessDescription.client)
        
        # In a session-based approach, we might not have access to all user preferences.
        # For this example, we'll assume all users want to receive notifications.
        dictForEventsAsOutput[clientID] = {
            "triggerEvent": True,
            EventsDescription.eventType: EventsDescription.projectEvent,
            EventsDescription.events: [{
                ProjectDescription.projectID: projectID,
                SessionContentSemperKI.processes: [{
                    ProcessDescription.processID: processID,
                    event: 1
                }]
            }]
        }

        if not clientOnly:
            contractorID = process.get(ProcessDescription.processDetails, {}).get(ProcessDetails.provisionalContractor)
            if contractorID:
                dictForEventsAsOutput[contractorID] = dictForEventsAsOutput[clientID]

        return dictForEventsAsOutput
    
    ##############################################
    @staticmethod
    def getAllProjectsFlat():
        """
        Return flat list of all projects, for admins

        :return: Json with all projects and their data
        :rtype: list
        """
        # In a session-based approach, we don't have access to all projects.
        # This method might need to be removed or significantly modified.
        raise NotImplementedError("getAllProjectsFlat is not applicable in a session-based approach")
    
    #############################################
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
            for fileKey in processObj.get(ProcessDescription.files, {}):
                if processObj[ProcessDescription.files][fileKey].get(FileObjectContent.remote, False):
                    return True
            return False
        except Exception as error:
            logger.error(f'could not check if files are remote: {str(error)}')
            return False
        
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
            
            dataEntry = {
                'dataID': dataID,
                'processID': processID,
                'type': typeOfData,
                'data': data,
                'details': details,
                'createdBy': createdBy,
                'contentID': IDofData,
                'createdWhen': str(timezone.now())
            }
            
            self.structuredSessionObj.currentSession['data_history'].append(dataEntry)
            self.structuredSessionObj.currentSession.modified = True

        except Exception as error:
            logger.error(f'could not create data entry: {str(error)}')
        
        return None
