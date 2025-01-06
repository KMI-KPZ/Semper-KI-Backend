"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logic for the processes
"""
import logging, numpy

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import manualCheckifAdmin

from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.definitions import ProcessDetails, PrioritiesForOrganizationSemperKI, PriorityTargetsSemperKI, ProcessDescription
from code_SemperKI.states.states import getButtonsForProcess, getMissingElements

from ..modelFiles.processModel import Process

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
####################################################################################
def logicForGetContractors(processObj:Process):
    """
    Get the contractors for the service

    :return: The contractors
    :rtype: tuple(list|Exception, int)
    """
    try:
        # TODO: if contractor is already selected, use that with all saved details

        serviceType = processObj.serviceType
        service = serviceManager.getService(processObj.serviceType)
        
        if serviceType == serviceManager.getNone():
            raise (Exception("No Service selected!"), 400)

        listOfFilteredContractors, transferObject = service.getFilteredContractors(processObj)
        
        # Format coming back from SPARQL is [{"ServiceProviderName": {"type": "literal", "value": "..."}, "ID": {"type": "literal", "value": "..."}}]
        # Therefore parse it
        listOfResultingContractors = []
        for contractor in listOfFilteredContractors:
            idOfContractor = ""
            if "ID" in contractor:
                idOfContractor = contractor["ID"]["value"]
            else:
                idOfContractor = contractor
            priceOfContractor = service.calculatePriceForService(processObj, {"orgaID": idOfContractor}, transferObject)
            contractorContentFromDB = pgProfiles.ProfileManagementOrganization.getOrganization(hashedID=idOfContractor)
            if isinstance(contractorContentFromDB, Exception):
                raise contractorContentFromDB
            contractorToBeAdded = {OrganizationDescription.hashedID: contractorContentFromDB[OrganizationDescription.hashedID],
                                   OrganizationDescription.name: contractorContentFromDB[OrganizationDescription.name],
                                   OrganizationDescription.details: contractorContentFromDB[OrganizationDescription.details],
                                   "price": priceOfContractor}
            listOfResultingContractors.append(contractorToBeAdded)
        
        #if settings.DEBUG:
        #    listOfResultingContractors.extend(pgProcesses.ProcessManagementBase.getAllContractors(serviceType))

        # Calculation of order of contractors based on priorities
        if ProcessDetails.priorities in processObj.processDetails:
            # This works since the order of keys in a dictionary is guaranteed to be the same as the insertion order for Python version >= 3.7
            userPrioritiesVector = [processObj.processDetails[ProcessDetails.priorities][entry][PriorityTargetsSemperKI.value] for entry in processObj.processDetails[ProcessDetails.priorities]]
        else:
            numberOfPriorities = len(PrioritiesForOrganizationSemperKI)
            userPrioritiesVector = [4 for i in range(numberOfPriorities)]
        listOfContractorsWithPriorities = []
        for entry in listOfResultingContractors:
            if OrganizationDetails.priorities in entry[OrganizationDescription.details]:
                prioList = []
                for priority in entry[OrganizationDescription.details][OrganizationDetails.priorities]:
                    prioList.append(entry[OrganizationDescription.details][OrganizationDetails.priorities][priority][PriorityTargetsSemperKI.value])
                # calculate vector 'distance' (I avoid the square root, see Wikipedia on euclidean distance)
                distanceFromUserPrios = numpy.sum(numpy.square(numpy.array(userPrioritiesVector) - numpy.array(prioList)))
                listOfContractorsWithPriorities.append((entry, distanceFromUserPrios))
        # sort ascending via distance (the shorter, the better)
        listOfContractorsWithPriorities.sort(key=lambda x: x[1])
        # parse for frontend
        listOfResultingContractors = []
        for contractor in listOfContractorsWithPriorities:
            listOfResultingContractors.append({
                OrganizationDescription.hashedID: contractor[0][OrganizationDescription.hashedID],
                OrganizationDescription.name: contractor[0][OrganizationDescription.name],
                OrganizationDetails.branding: contractor[0][OrganizationDescription.details][OrganizationDetails.branding],
                "price": contractor[0]["price"]
            })

        
        return (listOfResultingContractors, 200)

    except Exception as e:
        loggerError.error("Error in logicForGetContractors: %s" % e)
        return (e, 500)

####################################################################################
def logicForGetProcess(request, projectID, processID, functionName):
    """
    Get the process
    
    """
    try:
        contentManager = ManageContent(request.session)
        userID = contentManager.getClient()
        adminOrNot = manualCheckifAdmin(request.session)
        interface = contentManager.getCorrectInterface(functionName)
        if interface == None:
            return Exception("Rights not sufficient in getProcess"), 401
            

        process = interface.getProcessObj(projectID, processID)
        if isinstance(process, Exception):
            raise process

        # add buttons
        buttons = getButtonsForProcess(process, process.client == userID, adminOrNot) # calls current node of the state machine
        outDict = process.toDict()
        outDict["processStatusButtons"] = buttons

        # add what's missing to continue
        missingElements = getMissingElements(interface, process)
        outDict["processErrors"] = missingElements

        # parse for frontend
        outDict[ProcessDescription.serviceDetails] = serviceManager.getService(process.serviceType).parseServiceDetails(process.serviceDetails)
    
        return (outDict, 200)
    except Exception as e:
        loggerError.error("Error in logicForGetProcess: %s" % e)
        return (e, 500)