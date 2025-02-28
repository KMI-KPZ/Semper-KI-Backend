"""
Part of Semper-KI software

Silvio Weging 2025

Contains: Logic functions for service specific organization KG stuff
"""

import json, logging, copy
from datetime import datetime
from django.conf import settings

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementOrganization
from Generic_Backend.code_General.utilities.basics import checkIfRightsAreSufficient, checkIfUserIsLoggedIn, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from code_SemperKI.definitions import *
from code_SemperKI.utilities.basics import *
from code_SemperKI.connections.content.postgresql import pgKnowledgeGraph

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

##################################################
def logicForCloneTestGraphToOrgaForTests(request):
    """
    Clone the test graph to the organization graph for testing purposes
    """
    try:
        orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
        result = pgKnowledgeGraph.Basics.copyGraphForNewOwner(orgaID)
        if isinstance(result, Exception):
            raise result
    except Exception as e:
        loggerError.error("Error in logicForCloneTestGraphToOrgaForTests: " + str(e))
        return e