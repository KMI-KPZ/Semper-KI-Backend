"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for cryptographics
"""
import secrets, hashlib

#######################################################
def generateMD5(someString) -> str:
    """
    Convert string to md5 hashed string

    :param someString: String that shall be hashed
    :type someString: string
    :return: string containing the md5 hash
    :rtype: string

    """
    return hashlib.md5(someString.encode()).hexdigest()

#######################################################
def generateSalt(size = 5) -> str:
    """
    Generate unique random salt string to be attached to another string before hashing

    :param size: Number of characters generated as salt
    :type size: int
    :return: string containing salt
    :rtype: string

    """
    return secrets.token_hex(size)


