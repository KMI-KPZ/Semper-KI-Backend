"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logic for the Assembly service checking
"""
import logging, requests
import numpy as np
from stl import mesh
from io import BytesIO

from django.conf import settings

from rest_framework import status

from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists
from Generic_Backend.code_General.definitions import FileObjectContent
from Generic_Backend.code_General.utilities.crypto import EncryptionAdapter

from code_SemperKI.definitions import *
from code_SemperKI.handlers.public.files import getFileReadableStream
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.logics.processLogics import updateProcessFunction

from ..definitions import *

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")

####################################################################################

#######################################################
def checkIfSelectionIsAvailable(processObj):
    """
    Check if the selection really is available or not.
    Currently a dummy

    :param processObj: The process in question
    :type processObj: Process or ProcessInterface
    :return: True if everything is in order, False if something is missing
    :rtype: bool
    
    """
    serviceDetails = processObj.serviceDetails
    processDetails = processObj.processDetails
    # TODO
    return True