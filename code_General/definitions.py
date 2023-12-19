"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""
import enum

from .utilities.customStrEnum import StrEnumExactylAsDefined

from .modelFiles.organizationModel import OrganizationDescription
from .modelFiles.userModel import UserDescription

###################################################
# File Object
class FileObject():
    """
    How should a file Object look like?

    """
    id = ""
    path = ""
    fileName = ""
    tags = []
    date = ""
    licenses = []
    certificates = []
    URI = ""
    createdBy = ""

###################################################
# File object content as enum
class FileObjectContent(StrEnumExactylAsDefined):
    id = enum.auto()
    path = enum.auto()
    fileName = enum.auto()
    tags = enum.auto()
    date = enum.auto()
    licenses = enum.auto()
    certificates = enum.auto()
    URI = enum.auto()
    createdBy = enum.auto()

###################################################
# Enum for session content
class SessionContent(StrEnumExactylAsDefined):
    """
    What is saved into the session?

    """
    INITIALIZED = enum.auto()

    NUMBER_OF_LOGIN_ATTEMPTS = enum.auto()
    LAST_LOGIN_ATTEMPT = enum.auto()

    usertype = enum.auto()
    IS_PART_OF_ORGANIZATION = enum.auto()
    PG_PROFILE_CLASS = enum.auto()
    PATH_AFTER_LOGIN = enum.auto()
    MOCKED_LOGIN = enum.auto()
    ORGANIZATION_NAME = enum.auto()
    USER_ROLES = enum.auto()
    USER_PERMISSIONS = enum.auto()

###################################################
# Enum for types of users
class ProfileClasses(StrEnumExactylAsDefined):
    """
    Which classes exist?
    """
    user = enum.auto()
    organization = enum.auto()

###################################################
# Enum for Content of details for organizations
class OrganizationDetails(StrEnumExactylAsDefined):
    """
    What details can an organization have?
    
    """
    adress = enum.auto()
    email = enum.auto()
    taxID = enum.auto()