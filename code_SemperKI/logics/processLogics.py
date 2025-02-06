"""
Part of Semper-KI software

Silvio Weging 2024,
Akshay NS 2024

Contains: Logic for the processes
"""
import logging, numpy, copy, time

from datetime import datetime

from rest_framework.request import Request
from rest_framework import status

from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings

from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderServiceError
import asyncio
from asgiref.sync import sync_to_async, async_to_sync

from Generic_Backend.code_General.connections.postgresql import pgProfiles
from Generic_Backend.code_General.definitions import *
from Generic_Backend.code_General.utilities.basics import checkIfNestedKeyExists, manualCheckIfRightsAreSufficientForSpecificOperation, manualCheckifAdmin, manualCheckifLoggedIn
from Generic_Backend.code_General.utilities import crypto
from Generic_Backend.code_General.connections import s3

from code_SemperKI.states.states import StateMachine, signalDependencyToOtherProcesses, processStatusAsInt, ProcessStatusAsString
from code_SemperKI.connections.content.manageContent import ManageContent
from code_SemperKI.serviceManager import serviceManager, ServiceBase
from code_SemperKI.definitions import *
from code_SemperKI.states.states import getButtonsForProcess, getMissingElements, getFlatStatus
from code_SemperKI.connections.content.postgresql import pgProcesses
import code_SemperKI.utilities.websocket as WebSocketEvents

from ..modelFiles.processModel import Process, ProcessInterface

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
####################################################################################
async def calculateGeodesicDistance(userCoords:tuple, orgaCoords:tuple) -> tuple:
        """
        Calculate the geodesic distance between two addresses

        :param userCoords: The first address' coordinates
        :type userCoords: tuple
        :param orgaCoords: The second address' coordinates
        :type orgaCoords: tuple
        :return: The distance between the two coordinates
        :rtype: float | exception

        """
        try:
            if None not in userCoords and None not in orgaCoords and userCoords != (0,0) and orgaCoords != (0,0):
                distance = geodesic(userCoords, orgaCoords).kilometers
                return round(distance, 2)
            else:
                return -1.0

        except Exception as e:
            loggerError.error("Error in calculateGeodesicDistance: %s" % e)
            return -1.0
        
####################################################################################
def calculateAddInfoForEachContractor(contractor, processObj:Process|ProcessInterface, service:ServiceBase, savedCoords:tuple, transferObject:dict, idx:int):
    """
    Parallelized for loop over every contractor

    """
    try:
        # calculate price for service
        # await sync_to_async(
        if isinstance(contractor, tuple):
            contractorID = contractor[0] # contractor 0 contains the id, 1 contains if the contractor is verified and 2 contains a list of all groups that contractor can serve
        else:
            contractorID = contractor

        priceOfContractor = service.calculatePriceForService(processObj, {"contractor": contractor}, transferObject) #await asyncio.to_thread(service.calculatePriceForService, processObj, {"orgaID": contractorID}, transferObject)
        contractorContentFromDB = pgProfiles.ProfileManagementOrganization.getOrganization(hashedID=contractorID) #await asyncio.to_thread(pgProfiles.ProfileManagementOrganization.getOrganization, hashedID=contractorID)
        if isinstance(contractorContentFromDB, Exception):
            return {"error": contractorContentFromDB}
        
        coordsContractor = (0,0)
        if savedCoords == (0,0):
            distance = -1.0
        else:
            #retrieve addresses and calculate distance
            for idKey, entry in contractorContentFromDB[OrganizationDescription.details][OrganizationDetails.addresses].items():
                if Addresses.standard in entry and entry[Addresses.standard]:
                    if AddressesSKI.coordinates in entry:
                        coordsContractor = entry[AddressesSKI.coordinates]
                        break
                else:
                    if AddressesSKI.coordinates in entry:
                        coordsContractor = entry[AddressesSKI.coordinates]

            distance = async_to_sync(calculateGeodesicDistance)(savedCoords, coordsContractor) #await calculateGeodesicDistance(savedCoords, coordsContractor)

        contractorToBeAdded = {OrganizationDescription.hashedID: contractorContentFromDB[OrganizationDescription.hashedID],
                                OrganizationDescription.name: contractorContentFromDB[OrganizationDescription.name],
                                OrganizationDescription.details: contractorContentFromDB[OrganizationDescription.details],
                                "distance": distance,
                                "contractorCoordinates": coordsContractor,
                                ProcessDetails.prices: priceOfContractor}
        # add service specific details
        contractorToBeAdded = serviceManager.getService(processObj.serviceType).getServiceSpecificContractorDetails(contractorToBeAdded, contractor)
        return contractorToBeAdded
    except Exception as e: 
        return {"error": e}

####################################################################################
def parallelLoop(listOfFilteredContractors, processObj:Process|ProcessInterface, service:ServiceBase, savedCoords:tuple, transferObject:dict):
    """
    The main loop
    
    """
    try:
        #return await asyncio.gather(*[calculateAddInfoForEachContractor(listOfFilteredContractors[i], processObj, service, savedCoords, transferObject, i) for i in range(len(listOfFilteredContractors))])
        return [calculateAddInfoForEachContractor(listOfFilteredContractors[i], processObj, service, savedCoords, transferObject, i) for i in range(len(listOfFilteredContractors))]
    except Exception as e:
        loggerError.error("Error in parallelLoop: %s" % e)
        return []
####################################################################################
def logicForGetContractors(processObj:Process):
    """
    Get the contractors for the service

    :return: The contractors
    :rtype: tuple(list|Exception, int)
    """
    try:
        serviceType = processObj.serviceType
        if serviceType == serviceManager.getNone():
            return Exception("No Service selected!"), 400
        
        service = serviceManager.getService(serviceType)

        coordsOfUser = (0,0)
        if ProcessDetails.clientDeliverAddress in processObj.processDetails:
            address1 = processObj.processDetails[ProcessDetails.clientDeliverAddress]
            if AddressesSKI.coordinates in address1:
                coordsOfUser = address1[AddressesSKI.coordinates]
        
        listOfFilteredContractors, transferObject = service.getFilteredContractors(processObj)
        if len(listOfFilteredContractors) == 0:
            return [], 200

        # Loop could be parallelized but tests fail if it is
        # This is due to django not closing the database calls correctly. If there is some other solution to to_thread above then by all means...
        listOfResultingContractors = parallelLoop(listOfFilteredContractors, processObj, service, coordsOfUser, transferObject) #asyncio.run(parallelLoop(listOfFilteredContractors, processObj, service, coordsOfUser, transferObject))
        
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
            if "error" in entry:
                raise entry["error"]
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
            processObj.processDetails[ProcessDetails.prices][contractor[0][OrganizationDescription.hashedID]] = copy.deepcopy(contractor[0][ProcessDetails.prices])
            # but parse away the details for the frontend
            del contractor[0][ProcessDetails.prices][PricesDetails.details]
            contractor[0][OrganizationDetails.branding] = contractor[0][OrganizationDescription.details][OrganizationDetails.branding] if OrganizationDetails.branding in contractor[0][OrganizationDescription.details] else {}
            del contractor[0][OrganizationDescription.details]
            listOfResultingContractors.append(contractor[0])
        processObj.save()
        return (listOfResultingContractors, 200)

    except Exception as e:
        loggerError.error("Error in logicForGetContractors: %s" % e)
        return (e, 500)

####################################################################################
def parseProcessOutputForFrontend(processObj:Process|ProcessInterface, contentManager:ManageContent, functionName:str):
    """
    Add stuff to the usual output of the process for the frontend

    :param processObj: The process object
    :type processObj: Process | ProcessInterface
    :param contentManager: The content manager
    :type contentManager: ManageContent
    :param functionName: The function name that called this
    :type functionName: str
    :return: The process and statusCode
    :rtype: tuple(dict|Exception, int)
    
    """
    try:
        userID = contentManager.getClient()
        adminOrNot = manualCheckifAdmin(contentManager.currentSession)
        interface = contentManager.getCorrectInterface(functionName)
        if interface == None:
            return Exception(f"Rights not sufficient in {functionName}"), 401
        # add buttons
        contractor = False
        if processObj.contractor is not None:
            contractor = processObj.contractor.hashedID == userID
        buttons = getButtonsForProcess(processObj, processObj.client == userID, contractor, adminOrNot) # calls current node of the state machine
        outDict = processObj.toDict()
        outDict[ProcessOutput.processStatusButtons] = buttons

        # add what's missing to continue
        missingElements = getMissingElements(interface, processObj)
        outDict[ProcessOutput.processErrors] = missingElements

        # Add who needs to do what
        outDict[ProcessOutput.flatProcessStatus] = getFlatStatus(processObj.processStatus, contentManager.getClient() == processObj.client)


        # parse for frontend
        if processObj.serviceType == serviceManager.getNone():
            outDict[ProcessDescription.serviceDetails] = {}
        else:
            outDict[ProcessDescription.serviceDetails] = serviceManager.getService(processObj.serviceType).parseServiceDetails(processObj.serviceDetails)
    
        # check if costs are there and if they should be shown
        if ProcessDetails.prices in processObj.processDetails:
            for contractorID in processObj.processDetails[ProcessDetails.prices]:
                if PricesDetails.details in processObj.processDetails[ProcessDetails.prices][contractorID]:
                    if not (adminOrNot or pgProcesses.ProcessManagementBase.checkIfCurrentUserIsContractorOfProcess(processObj.processID, userID)):
                        del outDict[ProcessDescription.processDetails][ProcessDetails.prices][contractorID][PricesDetails.details]
                    else:
                        outDict[ProcessDescription.processDetails][ProcessDetails.prices][contractorID][PricesDetails.details] = crypto.decryptObjectWithAES(settings.AES_ENCRYPTION_KEY, processObj.processDetails[ProcessDetails.prices][contractorID][PricesDetails.details])
        
        return (outDict, 200)
    except Exception as e:
        loggerError.error("Error in parseProcessOutputForFrontend: %s" % e)
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
        interface = contentManager.getCorrectInterface(functionName)
        process = interface.getProcessObj(projectID, processID)
        if isinstance(process, Exception):
            raise process
        
        outDict, statusCode = parseProcessOutputForFrontend(process, contentManager, functionName)
        if statusCode != 200:
            raise Exception("Error in parseProcessOutputForFrontend")
        
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
        if interface is None:
            return Exception(f"Rights not sufficient in {functionName}"), status.HTTP_401_UNAUTHORIZED
            
        client = contentManager.getClient()
        projectObj = interface.getProjectObj(projectID)
        if projectObj is None:
            return Exception("Project not found!"), 404
        if client != projectObj.client:
            return Exception("Not allowed to create process in this project!"), 401
        
        interface.createProcess(projectID, processID, client)

        # set default addresses here
        if manualCheckifLoggedIn(request.session):
            clientObject = pgProfiles.ProfileManagementBase.getUser(request.session)
            defaultAddress = {}
            if checkIfNestedKeyExists(clientObject, UserDescription.details, UserDetails.addresses):
                clientAddresses = clientObject[UserDescription.details][UserDetails.addresses]
                for key in clientAddresses:
                    entry = clientAddresses[key]
                    if entry[Addresses.standard]:
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
            loggerError.error("Rights not sufficient in updateProcess")
            return ("", False)
        
        client = contentManager.getClient()
        trueIDOfCurrentUser = interface.getActualUserID()
        
        for processID in processIDs:
            if not contentManager.checkRightsForProcess(processID):
                loggerError.error("Rights not sufficient in updateProcess")
                return ("", False)

            if "deletions" in changes:
                for elem in changes["deletions"]:
                    # exclude people not having sufficient rights for that specific operation
                    if client != GlobalDefaults.anonymous and (elem == ProcessUpdates.messages or elem == ProcessUpdates.files):
                        if not manualCheckIfRightsAreSufficientForSpecificOperation(request.session, "updateProcess", str(elem)):
                            loggerError.error("Rights not sufficient in updateProcess")
                            return ("", False)
                        
                    returnVal = interface.deleteFromProcess(projectID, processID, elem, changes["deletions"][elem], client)

                    if isinstance(returnVal, Exception):
                        raise returnVal

            if "changes" in changes:
                for elem in changes["changes"]:
                    # exclude people not having sufficient rights for that specific operation
                    if client != GlobalDefaults.anonymous and (elem == ProcessUpdates.messages or elem == ProcessUpdates.files) and not manualCheckIfRightsAreSufficientForSpecificOperation(request.session, "updateProcess", str(elem)):
                        loggerError.error("Rights not sufficient in updateProcess")
                        return ("", False)
                    fireEvent = False
                    # for websocket events
                    if client != GlobalDefaults.anonymous and (elem == ProcessUpdates.messages or elem == ProcessUpdates.files or elem == ProcessUpdates.processStatus or elem == ProcessUpdates.serviceStatus):
                        fireEvent = True
                    returnVal = interface.updateProcess(projectID, processID, elem, changes["changes"][elem], client)
                    if isinstance(returnVal, Exception):
                        raise returnVal
                    if fireEvent:
                        if elem == ProcessUpdates.messages:
                            WebSocketEvents.fireWebsocketEventsForProcess(projectID, processID, request.session, elem, returnVal, NotificationSettingsUserSemperKI.newMessage, creatorOfEvent=trueIDOfCurrentUser)
                        elif elem == ProcessUpdates.processStatus:
                            WebSocketEvents.fireWebsocketEventsForProcess(projectID, processID, request.session, elem, returnVal, NotificationSettingsUserSemperKI.statusChange, creatorOfEvent=trueIDOfCurrentUser)
                        else:
                            WebSocketEvents.fireWebsocketEventsForProcess(projectID, processID, request.session, elem, returnVal, creatorOfEvent=trueIDOfCurrentUser)
                    
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
def deleteProcessFunction(session, processIDs:list[str], projectID:str):
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
        if interface is None:
            loggerError.error("Rights not sufficient in deleteProcesses")
            return HttpResponse("Insufficient rights!", status=401)

        for processID in processIDs:
            # check visibility
            if not contentManager.checkRightsForProcess(processID):
                loggerError.error("Rights not sufficient in deleteProcesses")
                return HttpResponse("Insufficient rights!", status=401)
            # check accessability
            processClient = interface.getProcessObj(projectID, processID)
            if isinstance(processClient, Exception):
                raise processClient
            processClient = processClient.client
            if processClient != contentManager.getClient():
                loggerError.error("Rights not sufficient in deleteProcesses")
                return HttpResponse("Insufficient rights!", status=401)
            
            result = interface.deleteProcess(processID)
            if result is False:
                raise Exception("Error in deleteProcessFunction")
            logger.info(f"{Logging.Subject.USER},{pgProfiles.ProfileManagementBase.getUserName(session)},{Logging.Predicate.DELETED},deleted,{Logging.Object.OBJECT},process {processID}," + str(datetime.now()))
        return HttpResponse("Success")
    
    except Exception as e:
        return e
    
#######################################################
def logicForCloneProcesses(request:Request, oldProjectID:str, oldProcessIDs:list[str], functionName:str):
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
        newProjectDetails = oldProject.projectDetails
        newProjectDetails[ProjectDetails.title] = newProjectDetails[ProjectDetails.title] + "*"
        pgProcesses.ProcessManagementBase.updateProject(newProjectID, ProjectUpdates.projectDetails, newProjectDetails)
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
            if ProcessDetails.provisionalContractor in oldProcessDetails:
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
            if oldProcess.serviceType == serviceManager.getNone():
                continue # no service selected, skip the rest

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
            errorOrNone = pgProcesses.ProcessManagementBase.updateProcess(newProjectID, newProcessID, ProcessUpdates.processStatus, processStatusAsInt(ProcessStatusAsString.DRAFT), oldProcess.client)
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