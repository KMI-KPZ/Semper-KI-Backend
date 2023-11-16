"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""
import enum

###################################################
# Statuscodes
class ProcessStatus(enum.Enum):
    DRAFT = 0,
    WAITING_FOR_OTHER_PROCESS =  100,
    SERVICE_READY =  200,
    SERVICE_IN_PROGRESS =  201,
    SERVICE_COMPLICATION =  202,
    CONTRACTOR_SELECTED =  300,
    VERIFYING =  400,
    VERIFIED =  500,
    REQUESTED =  600,
    CLARIFICATION =  700,
    CONFIRMED_BY_CONTRACTOR =  800,
    REJECTED_BY_CONTRACTOR =  801,
    CONFIRMED_BY_CLIENT =  900,
    REJECTED_BY_CLIENT =  901,
    PRODUCTION =  1000,
    DELIVERY =  1100,
    DISPUTE =  1200,
    COMPLETED =  1300,
    FAILED =  1400,
    CANCELED =  1500



###################################################
# Data Types
class DataType(enum.Enum):
    STATUS = 1,
    MESSAGE = 2,
    FILE = 3

###################################################
# File Object
class FileObject():
    id = ""
    title = ""
    tags = []
    date = ""
    licenses = []
    certificates = []
    URI = ""
    createdBy = ""