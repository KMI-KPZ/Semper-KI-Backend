"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Service for rights management
"""

import json
from django.conf import settings

#######################################################
class Rights:
    """
    Manage the rights for every path.
    """
    rightsDict = {}

    #######################################################
    def __init__(self):
        with open(str(settings.BASE_DIR) + "/backend_django/rights.json") as rightsFile:
            tempDict = json.load(rightsFile)
            for entry in tempDict["Rights"]:
                self.rightsDict[entry["permission"]["context"]+":"+entry["permission"]["permission"]] = entry["paths"]
    
    #######################################################
    def checkIfAllowed(self, permissions, path):
        """
        Check if permission is sufficient for that path.

        :param permissions: Permissions of that user
        :type permissions: [str]
        :param path: The name of the function (usually handlers)
        :type path: Str
        :return: True of permission sufficient, false if not.
        :rtype: Bool
        """

        for permission in permissions:
            if path in self.rightsDict[permission["permission_name"]]:
                return True
        
        return False
    
    #######################################################

rightsManagement = Rights()