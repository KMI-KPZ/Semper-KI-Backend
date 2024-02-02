"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Offers an interface to access the session dictionary in a structured way
"""

from Generic_Backend.code_General.definitions import SessionContent
from ..definitions import SessionContentSemperKI

# TODO: only for processes and projects at the beginning

#######################################################
class StructuredSession():
    """
    Interface class that handles the session 

    """

    rawSession = {}

    #######################################################
    def __init__(self, session) -> None:
        """
        Initialize with existing session
        
        """

        self.rawSession = session

    #######################################################
    
    # TODO: get and set content via key
    # TODO: mimic interface from postgres