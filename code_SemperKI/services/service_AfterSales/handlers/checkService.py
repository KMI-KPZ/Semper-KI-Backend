"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Handlers 
"""

from code_SemperKI.connections.content.postgresql import pgProcesses

#######################################################
def checkIfSelectionIsAvailable(processObj:pgProcesses.Process|pgProcesses.ProcessInterface):
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