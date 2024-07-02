"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Manages the content of the session and the database
"""
from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient
from Generic_Backend.code_General.definitions import SessionContent, GlobalDefaults
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from code_SemperKI.utilities.basics import manualCheckIfUserMaySeeProcess, manualCheckIfUserMaySeeProject
from .session import ProcessManagementSession
import code_SemperKI.connections.content.postgresql.pgProcesses as PPManagement

#######################################################
class ManageContent():
    """
    Class that manages the content, either in session or in postgres
    
    """

    #######################################################
    def __init__(self, session) -> None:
        self.currentSession = session
        self.sessionManagement = ProcessManagementSession(session)
        self.postgresManagement = PPManagement.ProcessManagementBase(session)

    #######################################################
    def checkRightsForProject(self, projectID) -> bool:
        """
        Check if user may see project

        :param functionName: The name of the calling function
        :type functionName: str
        :param projectID: The projectID of the project in question
        :type projectID: str
        :return: True if the user belongs to the rightful, false if not
        :rtype: Bool

        """
        currentUserID = self.getClient()
        if currentUserID == GlobalDefaults.anonymous:
            return True
        elif manualCheckIfUserMaySeeProject(self.currentSession, currentUserID, projectID):
            return True
        
        return False

    #######################################################
    def checkRightsForProcess(self, processID) -> bool:
        """
        Check if user may see process

        :param processID: The processID of the process in question
        :type processID: str
        :return: True if the user belongs to the rightful, false if not
        :rtype: Bool

        """
        currentUserID = self.getClient()
        if currentUserID == GlobalDefaults.anonymous:
            return True
        elif manualCheckIfUserMaySeeProcess(self.currentSession, currentUserID, processID):
            return True
        
        return False
    
    #######################################################
    def checkRights(self, functionName) -> bool:
        """
        Check if user is logged in and function may be called

        :param functionName: The name of the calling function
        :type functionName: str
        :return: True if the user belongs to the rightful, false if not
        :rtype: Bool

        """
        if manualCheckifLoggedIn(self.currentSession) and manualCheckIfRightsAreSufficient(self.currentSession, functionName):
            return True
        else:
            return False

    #######################################################
    def getCorrectInterface(self, functionName=""):
        """
        Return the correct class interface
        
        :param functionName: The name of the calling function
        :type functionName: str
        :return: Either the session or the postgres interface
        :rtype: ProcessManagementSession | ProcessManagementBase | None

        """
        if manualCheckifLoggedIn(self.currentSession):
            if functionName != "":
                if manualCheckIfRightsAreSufficient(self.currentSession, functionName):
                    return self.postgresManagement
                else:
                    return None
            else:
                return self.postgresManagement
        else:
            self.currentSession.modified = True
            return self.sessionManagement
        
    #######################################################
    def getClient(self):
        """
        Get ID if logged in, "anonymous" if not

        :return: String with clientID
        :rtype: str

        """
        if manualCheckifLoggedIn(self.currentSession):
            return pgProfiles.profileManagement[self.currentSession[SessionContent.PG_PROFILE_CLASS]].getClientID(self.currentSession)
        else:
            return GlobalDefaults.anonymous
