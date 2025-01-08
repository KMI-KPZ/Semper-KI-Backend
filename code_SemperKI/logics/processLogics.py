"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Logic for the processes
"""
import logging, numpy, copy

from datetime import datetime

from rest_framework.request import Request
from rest_framework import status

from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists, manualCheckIfRightsAreSufficientForSpecificOperation, manualCheckifAdmin, manualCheckifLoggedIn
from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections import s3

from code_SemperKI.states.states import StateMachine, signalDependencyToOtherProcesses, processStatusAsInt, ProcessStatusAsString
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.serviceManager import serviceManager
from code_SemperKI.definitions import *
from code_SemperKI.states.states import getButtonsForProcess, getMissingElements
from code_SemperKI.connections.content.postgresql import pgProcesses
import code_SemperKI.utilities.websocket as WebSocketEvents

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
            return Exception("No Service selected!"), 400

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
                                   ProcessDetails.prices: priceOfContractor}
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
        processObj.processDetails[ProcessDetails.prices] = {}
        for contractor in listOfContractorsWithPriorities:
            # save this to database
            processObj.processDetails[ProcessDetails.prices][OrganizationDescription.hashedID] = contractor[0][ProcessDetails.prices]
            # but parse away the details for the frontend
            del contractor[0][ProcessDetails.prices][PricesDetails.details]
            listOfResultingContractors.append({
                OrganizationDescription.hashedID: contractor[0][OrganizationDescription.hashedID],
                OrganizationDescription.name: contractor[0][OrganizationDescription.name],
                OrganizationDetails.branding: contractor[0][OrganizationDescription.details][OrganizationDetails.branding],
                ProcessDetails.prices: contractor[0][ProcessDetails.prices]
            })

        return (listOfResultingContractors, 200)

    except Exception as e:
        loggerError.error("Error in logicForGetContractors: %s" % e)
        return (e, 500)

####################################################################################
def logicForGetProcess(request:Request, projectID:str, processID:str, functionName:str):
    """
    Get the process

    :param request: The request
    :type request: Request
    :param projectID: The project ID
    :type projectID: str
    :param processID: The process ID
    :type processID: str
    :param functionName: The function name
    :type functionName: str
    :return: The process and statusCode
    :rtype: tuple(dict|Exception, int)
    
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
        if process.serviceType == serviceManager.getNone():
            outDict[ProcessDescription.serviceDetails] = {}
        else:
            outDict[ProcessDescription.serviceDetails] = serviceManager.getService(process.serviceType).parseServiceDetails(process.serviceDetails)
    
        # check if costs are there and if they should be shown
        if ProcessDetails.prices in process.processDetails:
            if PricesDetails.details in process.processDetails[ProcessDetails.prices]:
                if not (adminOrNot or pgProcesses.ProcessManagementBase.checkIfCurrentUserIsContractorOfProcess(processID, userID)):
                    del outDict[ProcessDetails.prices][PricesDetails.details]
                else:
                    outDict[ProcessDetails.prices][PricesDetails.details] = crypto.decryptObjectWithAES(settings.AES_ENCRYPTION_KEY, process.processDetails[ProcessDetails.prices][PricesDetails.details])

        return (outDict, 200)
    except Exception as e:
        loggerError.error("Error in logicForGetProcess: %s" % e)
        return (e, 500)
    
####################################################################################
def logicForCreateProcessID(request:Request, projectID:str, functionName:str):
    """
    Create a process and an ID with it

    :param request: The request
    :type request: Request
    :param projectID: The project ID
    :type projectID: str
    :param functionName: The function name
    :type functionName: str
    :return: The processID and statusCode
    :rtype: tuple(dict|Exception, int)
    
    """
    try:
        # generate ID, timestamp and template for process
        processID = crypto.generateURLFriendlyRandomString()
        
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface(functionName)
        if interface == None:
            return Exception(f"Rights not sufficient in {functionName}"), status.HTTP_401_UNAUTHORIZED
            
        client = contentManager.getClient()
        interface.createProcess(projectID, processID, client)

        # set default addresses here
        if manualCheckifLoggedIn(request.session):
            clientObject = pgProfiles.ProfileManagementBase.getUser(request.session)
            defaultAddress = {}
            if checkIfNestedKeyExists(clientObject, UserDescription.details, UserDetails.addresses):
                clientAddresses = clientObject[UserDescription.details][UserDetails.addresses]
                for key in clientAddresses:
                    entry = clientAddresses[key]
                    if entry["standard"]:
                        defaultAddress = entry
                        break
            addressesForProcess = {ProcessDetails.clientDeliverAddress: defaultAddress, ProcessDetails.clientBillingAddress: defaultAddress}
            errorOrNot = interface.updateProcess(projectID, processID, ProcessUpdates.processDetails, addressesForProcess, client)
            if isinstance(errorOrNot, Exception):
                raise errorOrNot
        # set default priorities here
        userPrioritiesObject = { prio:{PriorityTargetsSemperKI.value: 4} for prio in PrioritiesForOrganizationSemperKI}
        errorOrNot = interface.updateProcess(projectID, processID, ProcessUpdates.processDetails, {ProcessDetails.priorities: userPrioritiesObject}, client)
        if isinstance(errorOrNot, Exception):
            raise errorOrNot
        # set default title of the process
        errorOrNot = interface.updateProcess(projectID, processID, ProcessUpdates.processDetails, {ProcessDetails.title: processID[:10]}, client)
        if isinstance(errorOrNot, Exception):
            raise errorOrNot


        logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.CREATED},created,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

        #return just the id for the frontend
        output = {ProcessDescription.processID: processID}

        return (output, 200)
    except Exception as e:
        loggerError.error("Error in logicsForCreateProcessID: %s" % e)
        return (e, 500)
    
####################################################################################
######################################
#updateProcessFunction
def updateProcessFunction(request:Request, changes:dict, projectID:str, processIDs:list[str]):
    """
    Update process logic
    
    :param projectID: Project ID
    :type projectID: Str
    :param projectID: Process ID
    :type projectID: Str
    :return: Message if it worked or not
    :rtype: Str, bool or Error
    """
    try:
        contentManager = ManageContent(request.session)
        interface = contentManager.getCorrectInterface("updateProcess")
        if interface == None:
            logger.error("Rights not sufficient in updateProcess")
            return ("", False)
        
        client = contentManager.getClient()
        
        for processID in processIDs:
            if not contentManager.checkRightsForProcess(processID):
                logger.error("Rights not sufficient in updateProcess")
                return ("", False)

            if "deletions" in changes:
                for elem in changes["deletions"]:
                    # exclude people not having sufficient rights for that specific operation
                    if client != GlobalDefaults.anonymous and (elem == ProcessUpdates.messages or elem == ProcessUpdates.files):
                        if not manualCheckIfRightsAreSufficientForSpecificOperation(request.session, "updateProcess", str(elem)):
                            logger.error("Rights not sufficient in updateProcess")
                            return ("", False)
                        
                    returnVal = interface.deleteFromProcess(projectID, processID, elem, changes["deletions"][elem], client)

                    if isinstance(returnVal, Exception):
                        raise returnVal

            if "changes" in changes:
                for elem in changes["changes"]:
                    fireEvent = False
                    # for websocket events
                    if client != GlobalDefaults.anonymous and (elem == ProcessUpdates.messages or elem == ProcessUpdates.files or elem == ProcessUpdates.processStatus or elem == ProcessUpdates.serviceStatus):
                        # exclude people not having sufficient rights for that specific operation
                        if (elem == ProcessUpdates.messages or elem == ProcessUpdates.files) and not manualCheckIfRightsAreSufficientForSpecificOperation(request.session, "updateProcess", str(elem)):
                            logger.error("Rights not sufficient in updateProcess")
                            return ("", False)
                        fireEvent = True
                    returnVal = interface.updateProcess(projectID, processID, elem, changes["changes"][elem], client)
                    if isinstance(returnVal, Exception):
                        raise returnVal
                    if fireEvent:
                        if elem == ProcessUpdates.messages:
                            WebSocketEvents.fireWebsocketEventsForProcess(projectID, processID, request.session, elem, returnVal, NotificationSettingsUserSemperKI.newMessage)
                        elif elem == ProcessUpdates.processStatus:
                            WebSocketEvents.fireWebsocketEventsForProcess(projectID, processID, request.session, elem, returnVal, NotificationSettingsUserSemperKI.statusChange)
                        else:
                            WebSocketEvents.fireWebsocketEventsForProcess(projectID, processID, request.session, elem, returnVal)
                    
            # change state for this process if necessary
            process = interface.getProcessObj(projectID, processID)
            currentState = StateMachine(initialAsInt=process.processStatus)
            currentState.onUpdateEvent(interface, process)
            signalDependencyToOtherProcesses(interface, process)

            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(request.session)},{Logging.Predicate.EDITED},updated,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))

        return ("", True)
    except (Exception) as error:
        return (error, True)       
    
#######################################################
#deleteProcessFunction
def deleteProcessFunction(session, processIDs:list[str]):
    """
    Delete the processes

    :param session: The session
    :type session: Django session object (dict-like)
    :param processIDs: Array of proccess IDs 
    :type processIDs: list[str]
    :return: The response
    :rtype: HttpResponse | Exception

    """
    try:
        contentManager = ManageContent(session)
        interface = contentManager.getCorrectInterface("deleteProcesses")
        if interface == None:
            logger.error("Rights not sufficient in deleteProcesses")
            return HttpResponse("Insufficient rights!", status=401)

        for processID in processIDs:
            if not contentManager.checkRightsForProcess(processID):
                logger.error("Rights not sufficient in deleteProcesses")
                return HttpResponse("Insufficient rights!", status=401)
            interface.deleteProcess(processID)
            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))
        return HttpResponse("Success")
    
    except Exception as e:
        return e
    
#######################################################
def logicForCloneProcess(request:Request, oldProjectID:str, oldProcessIDs:list[str], functionName:str):
    """
    Duplicate selected processes. Works only for logged in users.

    :param request: POST request from statusButtonRequest
    :type request: HTTP POST
    :param projectID: The project ID of the project the processes belonged to
    :type projectID: str
    :param processIDs: List of processes to be cloned
    :type processIDs: list of strings
    :param functionName: The function name
    :type functionName: str
    :return: ResultDict or Exception and statusCode
    :rtype: tuple(dict|Exception, int)
    
    """
    try:
        outDict = {"projectID": "", "processIDs": []}

        # create new project with old information
        oldProject = pgProcesses.ProcessManagementBase.getProjectObj(oldProjectID)
        newProjectID = crypto.generateURLFriendlyRandomString()
        outDict["projectID"] = newProjectID
        errorOrNone = pgProcesses.ProcessManagementBase.createProject(newProjectID, oldProject.client)
        if isinstance(errorOrNone, Exception):
            raise errorOrNone
        pgProcesses.ProcessManagementBase.updateProject(newProjectID, ProjectUpdates.projectDetails, oldProject.projectDetails)
        if isinstance(errorOrNone, Exception):
            raise errorOrNone
        
        mapOfOldProcessIDsToNewOnes = {}
        # for every old process, create new process with old information
        for processID in oldProcessIDs:
            oldProcess = pgProcesses.ProcessManagementBase.getProcessObj(oldProjectID, processID) 
            newProcessID = crypto.generateURLFriendlyRandomString()
            outDict["processIDs"].append(newProcessID)
            mapOfOldProcessIDsToNewOnes[processID] = newProcessID
            errorOrNone = pgProcesses.ProcessManagementBase.createProcess(newProjectID, newProcessID, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            
            oldProcessDetails = copy.deepcopy(oldProcess.processDetails)
            del oldProcessDetails[ProcessDetails.provisionalContractor]
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.processDetails, oldProcessDetails, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            
            # copy files but with new fileID
            newFileDict = {}
            for fileKey in oldProcess.files:
                oldFile = oldProcess.files[fileKey]
                newFile = copy.deepcopy(oldFile)
                #newFileID = crypto.generateURLFriendlyRandomString()
                newFile[FileObjectContent.id] = fileKey
                newFilePath = newProcessID+"/"+fileKey
                newFile[FileObjectContent.path] = newFilePath
                newFile[FileObjectContent.date] = str(timezone.now())
                if FileObjectContent.isFile not in newFile or newFile[FileObjectContent.isFile]:
                    if oldFile[FileObjectContent.remote]:
                        s3.manageRemoteS3.copyFile("kiss/"+oldFile[FileObjectContent.path], newFilePath)
                    else:
                        s3.manageLocalS3.copyFile(oldFile[FileObjectContent.path], newFilePath)
                newFileDict[fileKey] = newFile
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.files, newFileDict, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            
            # set service specific stuff
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.serviceType, oldProcess.serviceType, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            # set service details -> implementation in service (cloneServiceDetails)
            newProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, newProcessID) 
            errorOrNewDetails = serviceManager.getService(oldProcess.serviceType).cloneServiceDetails(oldProcess.serviceDetails, newProcess)
            if isinstance(errorOrNewDetails, Exception):
                raise errorOrNewDetails
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.serviceDetails, errorOrNewDetails, oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone

        # all new processes must already be created here in order to link them accordingly
        for oldProcessID, newProcessID in mapOfOldProcessIDsToNewOnes.items():
            oldProcess = pgProcesses.ProcessManagementBase.getProcessObj(oldProjectID, oldProcessID)
            newProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, newProcessID)
            # connect the processes if they where dependend before
            for connectedOldProcessIn in oldProcess.dependenciesIn.all():
                if connectedOldProcessIn.processID in oldProcessIDs:
                    newConnectedProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, mapOfOldProcessIDsToNewOnes[connectedOldProcessIn.processID])
                    newProcess.dependenciesIn.add(newConnectedProcess)
            for connectedOldProcessIn in oldProcess.dependenciesOut.all():
                if connectedOldProcessIn.processID in oldProcessIDs:
                    newConnectedProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, mapOfOldProcessIDsToNewOnes[connectedOldProcessIn.processID])
                    newProcess.dependenciesOut.add(newConnectedProcess)
            newProcess.save()

            # set process state through state machine (could be complete or waiting or in conflict and so on)
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.SERVICE_IN_PROGRESS), oldProcess.client)
            if isinstance(errorOrNone, Exception):
                raise errorOrNone
            newProcess = pgProcesses.ProcessManagementBase.getProcessObj(newProjectID, newProcessID)
            currentState = StateMachine(initialAsInt=newProcess.processStatus)
            contentManager = ManageContent(request.session)
            interface = contentManager.getCorrectInterface(functionName)
            currentState.onUpdateEvent(interface, newProcess)

        return (outDict, 200)
    except Exception as e:
        loggerError.error("Error in logicForCloneProcess: %s" % e)
        return (e, 500)