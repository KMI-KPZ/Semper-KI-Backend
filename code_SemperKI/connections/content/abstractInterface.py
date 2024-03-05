"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Abstract interface for content of session and database
"""

from abc import ABC, abstractmethod

from ...definitions import ProjectUpdates, ProcessUpdates

#######################################################
class AbstractContentInterface(ABC):
    """
    Abstract class with functions that session and postgres interfaces have to comply to
    
    """

    ###################################################
    @abstractmethod
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
        pass

    #######################################################
    @abstractmethod
    def getProjectObj(self, projectID:str):
        """
        Return the project and all its details

        :param projectID: The ID of the project
        :type projectID: str
        :return: Project Object
        :rtype: ProjectInterface | Project | None
        
        """
        pass

    #######################################################
    @abstractmethod
    def getProject(self, projectID:str):
        """
        Get info about one project.

        :param projectID: ID of the project
        :type projectID: str
        :return: dict with info about that project
        :rtype: dict

        """
        pass

    ##############################################
    @abstractmethod
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
        pass

    #######################################################
    @abstractmethod
    def deleteProject(self, projectID:str):
        """
        Delete specific project.

        :param projectID: unique project ID to be deleted
        :type projectID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        pass

    ##############################################
    @abstractmethod
    def getProjectsFlat(self, session):
        """
        Get all projects for that user but with limited detail.

        :param session: session of that user
        :type session: dict
        :return: sorted list with projects
        :rtype: list

        """
        pass

########################################################
    ###################################################
    @abstractmethod
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
        pass

    ####################################################
    @abstractmethod
    def getProcessObj(self, projectID:str, processID:str):
        """
        Return the process and all its details

        :param projectID: The ID of the project
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :return: Process Object
        :rtype: ProcessInterface | Process | None

        """
        pass

    ###################################################
    @abstractmethod
    def deleteProcess(self, processID:str, processObj=None):
        """
        Delete specific process.

        :param processID: unique process ID to be deleted
        :type processID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        pass

    ##############################################
    @abstractmethod
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
        pass

    ##############################################
    @abstractmethod
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
        pass

    ##############################################
    @abstractmethod
    def getUserID(self) -> str:
        """
        Retrieve UserID from session
        
        :return: UserID
        :rtype: str
        """
        pass