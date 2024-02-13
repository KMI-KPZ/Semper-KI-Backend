"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Offers an interface to access the session dictionary in a structured way
"""

from django.utils import timezone
import logging

from Generic_Backend.code_General.definitions import SessionContent, FileObjectContent
from Generic_Backend.code_General.connections import s3

from ...definitions import SessionContentSemperKI
from ...definitions import ProjectUpdates, ProcessUpdates
from ...modelFiles.processModel import ProcessInterface, ProcessDescription
from ...modelFiles.projectModel import ProjectInterface, ProjectDescription
from .abstractInterface import AbstractContentInterface

logger = logging.getLogger("errors")

#######################################################
class StructuredSession():
    """
    Interface class that handles the session content

    """

    currentSession = {}

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
    def getProject(self, projectID:str) -> dict:
        """
        Return specific project from session

        :param projectID: The ID of the project
        :type projectID: str
        :return: Dictionary with project in it
        :rtype: dict

        """

        return self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]

    #######################################################
    def getProjects(self) -> list:
        """
        Return all projects from session

        :return: list with projects in it
        :rtype: list

        """

        return list(self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS])
    
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
        for projectID in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS]:
            if SessionContentSemperKI.processes in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID]:
                for currentProcessID in self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes]:
                    if currentProcessID == processID:
                        return self.currentSession[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][processID]

        return {}

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
            returnObj = ProjectInterface(projectID, content[ProjectDescription.createdWhen])
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

        self.structuredSessionObj.setProject(projectID, ProjectInterface(projectID, str(now)).toDict())
    
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
            savedProject = self.structuredSessionObj.getProject(projectID)
            return savedProject
        
        except (Exception) as error:
            logger.error(f'could not get project: {str(error)}')
            return {}

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
                currentProject[ProjectDescription.updatedWhen] = updated
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
            for currentProcess in self.structuredSessionObj.getProcesses(projectID):
                files = currentProcess[ProcessDescription.files]
                for fileObj in files:
                    s3.manageLocalS3.deleteFile(fileObj[FileObjectContent.id])
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
                allProjects[idx]["processesCount"] = len(self.structuredSessionObj.getProcesses(entry[ProjectDescription.projectID]))
                del allProjects[idx][SessionContentSemperKI.processes] # frontend doesn't need that
            
            return allProjects
        except (Exception) as error:
            logger.error(f"could not get all flat projects: {str(error)}")
            return error

    #######################################################
    def getProcessObj(self, projectID:str, processID:str):
        """
        Return the process and all its details

        :param projectID: The ID of the project
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :return: Process Object
        :rtype: ProcessInterface

        """
        try:
            content = self.structuredSessionObj.getProcess(projectID, processID)
            returnObj = ProcessInterface(processID, content[ProcessDescription.createdWhen])
            returnObj.setValues(content[ProcessDescription.processDetails], content[ProcessDescription.processStatus], content[ProcessDescription.serviceDetails], content[ProcessDescription.serviceStatus], content[ProcessDescription.serviceType], content[ProcessDescription.client], content[ProcessDescription.files], content[ProcessDescription.messages], content[ProcessDescription.updatedWhen], content[ProcessDescription.accessedWhen])
            return returnObj
        except (Exception) as error:
            logger.error(f"Could not fetch process: {str(error)}")
            return error

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

        self.structuredSessionObj.setProcess(projectID, processID, ProcessInterface(processID, str(now)).toDict())

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
            for fileObj in files:
                s3.manageLocalS3.deleteFile(fileObj[FileObjectContent.id])
            self.structuredSessionObj.deleteProcess(processID)

        except (Exception) as error:
            logger.error(f'could not delete project: {str(error)}')
            return error

    ##############################################
    # TODO
    
    def updateProcess(self, processID:str, updateType: ProcessUpdates, content:dict, updatedBy:str):
        """
        Change details of a process like its status, or save communication. 

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
        pass

    ##############################################
    #TODO
    
    def deleteFromProcess(self, processID:str, updateType: ProcessUpdates, content:dict, deletedBy:str):
        """
        Delete details of a process like its status, or content. 

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
        pass