"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Manages the content of the session and the database
"""

from Generic_Backend.code_General.utilities.basics import manualCheckifLoggedIn, manualCheckIfRightsAreSufficient
from Generic_Backend.code_General.definitions import SessionContent, GlobalDefaults
from Generic_Backend.code_General.connections.postgresql import pgProfiles

from .session import ProcessManagementSession
from .postgresql.pgProcesses import ProcessManagementBase

#######################################################
class ManageContent():
    """
    Class that manages the content, either in session or in postgres
    
    """

    #######################################################
    def __init__(self, session) -> None:
        self.currentSession = session
        self.sessionManagement = ProcessManagementSession(session)
        self.postgresManagement = ProcessManagementBase()

    #######################################################
    def getCorrectInterface(self, functionName:str):
        """
        Return the correct class interface
        
        :param functionName: The name of the calling function
        :type functionName: str
        :return: Either the session or the postgres interface
        :rtype: ProcessManagementSession | ProcessManagementBase

        """
        if manualCheckifLoggedIn(self.currentSession) and manualCheckIfRightsAreSufficient(self.currentSession, functionName):
            return self.postgresManagement
        else:
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
