"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Definitions, Classes, Enums to describe Elements in the Backend as well as Services
"""
import enum

###################################################
# File Object
class FileObject():
    """
    How should a file Object look like?

    """
    id = ""
    title = ""
    tags = []
    date = ""
    licenses = []
    certificates = []
    URI = ""
    createdBy = ""