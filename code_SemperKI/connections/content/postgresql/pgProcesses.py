"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls
"""
import enum

from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from Generic_Backend.code_General.utilities import basics
from Generic_Backend.code_General.modelFiles.userModel import User
from Generic_Backend.code_General.modelFiles.organizationModel import Organization
from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementBase, profileManagement
from Generic_Backend.code_General.definitions import FileObjectContent, OrganizationDescription, SessionContent, OrganizationDetails, GlobalDefaults
from Generic_Backend.code_General.connections import s3
from Generic_Backend.code_General.utilities import crypto


from ....modelFiles.projectModel import Project, ProjectInterface
from ....modelFiles.processModel import Process, ProcessInterface
from ....modelFiles.dataModel import Data

from ....definitions import *

from ....serviceManager import serviceManager

from ..abstractInterface import AbstractContentInterface

import logging
logger = logging.getLogger("errors")


####################################################################################
# Projects/Processes general
class ProcessManagementBase(AbstractContentInterface):
    
    ##############################################
    @staticmethod
    def checkIfUserIsClient(userHashID, projectID="", processID=""):
        """
        See if the user is the client of either the project or the process

        :param userHashID: The hashed ID of the user/organization
        :type userHashID: Str
        :param projectID: The ID of the project
        :type projectID: Str
        :param processID: The ID of the process
        :type processID: Str
        :return: True if user is client, false if not
        :rtype: Bool
        
        """
        if projectID != "":
            projectObj = Project.objects.get(projectID=projectID)
            if projectObj.client == userHashID:
                return True
            else: 
                return False
        if processID != "":
            processObj = Process.objects.get(processID=processID)
            if processObj.client == userHashID:
                return True
            else:
                return False
        return False

    ##############################################
    @staticmethod
    def getData(processID, processObject=None):
        """
        Get all files.

        :param processID: process ID for a process
        :type processID: str
        :return: list of all data
        :rtype: list
        
        """

        try:
            if processObject != None:
                processObj = processObject
            else:
                processObj = Process.objects.filter(processID=processID)
            dates = processObj.data.all()
            outList = []
            for datum in dates:
                outList.append(datum.toDict())
            return outList
        except (Exception) as error:
            logger.error(f'Generic error in getData: {str(error)}')

        return []
    
    ##############################################
    @staticmethod
    def getDataWithContentID(processID, IDofContent):
        """
        Get one datum in particular but use the content ID.

        :param processID: process ID for a process
        :type processID: str
        :param IDofContent: ID for a datum
        :type IDofContent: str
        :return: this datum
        :rtype: dict
        
        """

        try:
            processObj = Process.objects.filter(processID=processID)
            date = processObj.data.filter(contentID=IDofContent)
            return date.toDict()
        except (Exception) as error:
            logger.error(f'Generic error in getDataWithID: {str(error)}')

        return {}
    
    ##############################################
    @staticmethod
    def getDataWithID(IDofData):
        """
        Get one datum in particular.

        :param IDofData: ID for a datum
        :type IDofData: str
        :return: this datum
        :rtype: dict
        
        """

        try:
            date = Data.objects.get(dataID=IDofData)
            return date.toDict()
        except (Exception) as error:
            logger.error(f'Generic error in getDataWithID: {str(error)}')

        return {}
    
    ##############################################
    @staticmethod
    def getDataByType(typeOfData:DataType, processID, processObject = None):
        """
        Get all data of a certain type for a process.

        :param processID: process ID for a process
        :type processID: str
        :param typeOfData: type of this data
        :type typeOfData: DataType
        :return: all results
        :rtype: list
        
        """

        try:
            if processObject != None:
                processObj = processObject
            else:
                processObj = Process.objects.get(processID=processID)
            dates = processObj.data.filter(type=typeOfData)
            outList = []
            for datum in dates:
                outList.append(datum.toDict())
            return outList
        except (Exception) as error:
            logger.error(f'Generic error in getDataByType: {str(error)}')

        return []

    ##############################################
    @staticmethod
    def createDataEntry(data, dataID, processID, typeOfData:DataType, createdBy:str, details={}, IDofData=""):
        """
        Create an entry in the Data table

        :param data: The data itself
        :type data: Dict in JSON
        :param dataID: The ID of that date
        :type dataID: Str
        :param processID: process it belongs to
        :type processID: str
        :param typeOfData: The type of this data
        :type typeOfData: DataType
        :param createdBy: Who created it (hashed ID)
        :type createdBy: Str
        :param details: Some metadata
        :type details: JSON Dict
        :param IDofData: If the data has an id, save it
        :type IDofData: Str
        :return: Nothing
        :rtype: None
        """
        try:
            currentProcess = Process.objects.get(processID=processID)
            createdDataEntry = Data.objects.create(dataID=dataID, process=currentProcess, type=typeOfData, data=data, details=details, createdBy=createdBy, contentID=IDofData, updatedWhen=timezone.now())

        except (Exception) as error:
            logger.error(f'could not create data entry: {str(error)}')
        
        return None
    
    ##############################################
    @staticmethod
    def deleteDataEntry(dataID):
        """
        Delete a specific data entry

        :param dataID: The primary key of that datum
        :type dataID: str
        :return: Nothing
        :rtype: None
        """
        try:
            affectedEntries = Data.objects.delete(dataID=dataID)
        except (Exception) as error:
            logger.error(f'could not delete data entry: {str(error)}')
        
        return None

    ##############################################
    @staticmethod
    def getProcessObj(processID):
        """
        Get one process.

        :param processID: process ID for a process
        :type processID: str
        :return: Requested process
        :rtype: ProcessObj

        """
        try:
            currentProcess = Process.objects.get(processID=processID)
            return currentProcess
        except (ObjectDoesNotExist) as error:
            return None
        except (Exception) as error:
            logger.error(f'could not get process object: {str(error)}')
        
        return None
    
    ##############################################
    @staticmethod
    def getProjectObj(projectID):
        """
        Get one project object.

        :param projectID: project ID for a project 
        :type projectID: str
        :return: Requested project object
        :rtype: project

        """
        try:
            currentProject = Project.objects.get(projectID=projectID)
            return currentProject
        except (ObjectDoesNotExist) as error:
            return None
        except (Exception) as error:
            logger.error(f'could not get project object: {str(error)}')
        
        return None

    ##############################################
    @staticmethod
    def getProject(projectID):
        """
        Get info about one project.

        :param projectID: ID of the project
        :type projectID: str
        :return: dict with info about that project
        :rtype: dict

        """
        try:
            # TODO - remove stuff for frontend etc
            # get project
            projectObj = Project.objects.get(projectID=projectID)

            output = projectObj.toDict()

            processesOfThatProject = []
            for entry in projectObj.processes.all():
                processesOfThatProject.append(entry.toDict())

            output[SessionContentSemperKI.processes] = processesOfThatProject
            
            return output

        except (Exception) as error:
            logger.error(f'could not get project: {str(error)}')
        
        return {}

    ##############################################
    @staticmethod
    def getProjectForContractor(projectID, contractorHashID):
        """
        Get info about one project for an organization as a contractor.

        :param projectID: ID of the project
        :type projectID: str
        :param contractorHashID: The ID of the contractor
        :type contractorHashID: str
        :return: dict with info about that project
        :rtype: dict

        """
        try:
            # TODO - remove stuff for frontend etc
            # get project
            projectObj = Project.objects.get(projectID=projectID)

            output = projectObj.toDict()

            processesOfThatProject = []
            for entry in projectObj.processes.all():
                if entry.contractor != None and entry.contractor.hashedID == contractorHashID:
                    processesOfThatProject.append(entry.toDict())

            output[SessionContentSemperKI.processes] = processesOfThatProject
            
            return output

        except (Exception) as error:
            logger.error(f'could not get project: {str(error)}')
        
        return {}
    
    ##############################################
    @staticmethod
    def getAllUsersOfProject(projectID):
        """
        Get all user IDs that are connected to that project.

        :param projectID: unique project ID
        :type projectID: str
        :return: Set of all user IDs
        :rtype: Set

        """
        try:
            currentProject = Project.objects.get(projectID=projectID)
            users = set()
            userObj, orgaOrUser = ProfileManagementBase.getUserViaHash(currentProject.client)
            if userObj != None:
                if orgaOrUser:
                    # Is organization, add all people
                    for user in userObj.users.all():
                        users.update({user.hashedID})
                users.update({userObj.hashedID})

            return users
        except (Exception) as error:
            logger.error(f'could not get all users of project: {str(error)}')
        return set()

    ##############################################
    @staticmethod
    def getAllUsersOfProcess(processID):
        """
        Get all user IDs that are connected to that processID.

        :param processID: unique process ID
        :type processID: str
        :return: Set of all user IDs
        :rtype: Set

        """
        try:
            currentProcess = Process.objects.get(processID=processID)
            users = set()
            userObj, orgaOrUser = ProfileManagementBase.getUserViaHash(currentProcess.client)
            if userObj != None:
                if orgaOrUser:
                    # Is organization, add all people
                    for user in userObj.users.all():
                        users.update({user.hashedID})
                users.update({userObj.hashedID})
            if currentProcess.contractor != None:
                for user in currentProcess.contractor.users.all():
                    users.update({user.hashedID})
                users.update({currentProcess.contractor.hashedID})

            return users
        except (Exception) as error:
            logger.error(f'could not get all users of process: {str(error)}')
        return set()
    
    ##############################################
    @staticmethod
    def getProjectIDViaProcessID(processID):
        """
        Get Project ID from the Process ID

        :param processID: unique process ID
        :type processID: str
        :return: project ID
        :rtype: str
        """
        try:
            currentProcess = Process.objects.get(processID=processID)
            return currentProcess.project.projectID
        except (Exception) as error:
            logger.error(f'could not get project ID via process ID: {str(error)}')
            return ""

    ##############################################
    @staticmethod
    def deleteProcess(processID, processObj=None):
        """
        Delete specific process.

        :param processID: unique process ID to be deleted
        :type processID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            if processObj != None:
                currentProcess = processObj
            else:
                currentProcess = Process.objects.get(processID=processID)

            allFiles = currentProcess.files
            # delete files as well
            for entry in allFiles:
                s3.manageLocalS3.deleteFile(allFiles[entry][FileObjectContent.path])
            
            # if that was the last process, delete the project as well
            # if len(currentProcess.project.processes.all()) == 1:
            #     currentProcess.project.delete()
            # else:
            currentProcess.project.updatedWhen = updated
            currentProcess.delete()
            #currentProcess.save()
            return True
        except (ObjectDoesNotExist) as error:
            return None
        except (Exception) as error:
            logger.error(f'could not delete process: {str(error)}')
        return False
    
    ##############################################
    @staticmethod
    def deleteProject(projectID):
        """
        Delete specific project.

        :param projectID: unique project ID to be deleted
        :type projectID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            #currentUser = User.objects.get(hashedID=userID)
            currentProject = Project.objects.get(projectID=projectID)

            # delete all files from every process as well
            for process in currentProject.processes.all():
                ProcessManagementBase.deleteProcess(process.processID, processObj=process)

            currentProject.delete()
            #currentProject.save()
            return True
        except (ObjectDoesNotExist) as error:
            return None
        except (Exception) as error:
            logger.error(f'could not delete project: {str(error)}')
        return False

    ##############################################
    @staticmethod
    def updateProject(projectID, updateType: ProjectUpdates, content):
        """
        Change details of an project like its status. 

        :param projectID: project ID that this project belongs to
        :type projectID: str
        :param updateType: changed project details
        :type updateType: EnumUpdates
        :param content: changed project, can be many stuff
        :type content: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            if updateType == ProjectUpdates.projectStatus:
                currentProject = Project.objects.get(projectID=projectID)
                currentProject.projectStatus = content
                currentProject.updatedWhen = updated
                currentProject.save()

            elif updateType == ProjectUpdates.projectDetails:
                currentProject = Project.objects.get(projectID=projectID)
                for key in content:
                    currentProject.projectDetails[key] = content[key]
                currentProject.updatedWhen = updated
                currentProject.save()
            return True
        except (Exception) as error:
            logger.error(f'could not update project: {str(error)}')
            return error
    
    ##############################################
    @staticmethod
    def updateProcess(projectID, processID, updateType: ProcessUpdates, content, updatedBy):
        """
        Change details of a process like its status, or save communication. 

        :param projectID: The project ID, not necessary here
        :type projectID: str
        :param processID: unique processID to be edited
        :type processID: str
        :param updateType: changed process details
        :type updateType: EnumUpdates
        :param content: changed process, can be many stuff
        :type content: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            currentProcess = Process.objects.get(processID=processID)
            currentProcess.updatedWhen = updated
            dataID = crypto.generateURLFriendlyRandomString()

            if updateType == ProcessUpdates.messages:
                currentProcess.messages["messages"].append(content)
                ProcessManagementBase.createDataEntry(content, dataID, processID, DataType.MESSAGE, updatedBy)
                
            elif updateType == ProcessUpdates.files:
                for entry in content:
                    currentProcess.files[content[entry][FileObjectContent.id]] = content[entry]
                    ProcessManagementBase.createDataEntry(content[entry], dataID, processID, DataType.FILE, updatedBy, {}, content[entry][FileObjectContent.id])

            elif updateType == ProcessUpdates.processStatus:
                currentProcess.processStatus = content
                ProcessManagementBase.createDataEntry(content, dataID, processID, DataType.STATUS, updatedBy)
                
            elif updateType == ProcessUpdates.processDetails:
                for entry in content:
                    currentProcess.processDetails[entry] = content[entry]
                ProcessManagementBase.createDataEntry(content, dataID, processID, DataType.DETAILS, updatedBy)

            elif updateType == ProcessUpdates.serviceType:
                currentProcess.serviceType = content
                ProcessManagementBase.createDataEntry(content, dataID, processID, DataType.OTHER, updatedBy, {ProcessUpdates.serviceType: ""})
                      
            elif updateType == ProcessUpdates.serviceStatus:
                currentProcess.serviceStatus = content
                ProcessManagementBase.createDataEntry(content, dataID, processID, DataType.STATUS, updatedBy, {ProcessUpdates.serviceStatus: ""})

            elif updateType == ProcessUpdates.serviceDetails:
                currentProcess.serviceDetails = serviceManager.getService(currentProcess.serviceType).updateServiceDetails(currentProcess.serviceDetails, content)
                ProcessManagementBase.createDataEntry(content, dataID, processID, DataType.DETAILS, updatedBy, {ProcessUpdates.serviceDetails: ""})

            elif updateType == ProcessUpdates.provisionalContractor:
                currentProcess.processDetails[ProcessDetails.provisionalContractor] = content
                ProcessManagementBase.createDataEntry(content, dataID, processID, DataType.OTHER, updatedBy, {ProcessUpdates.provisionalContractor: ""})

            currentProcess.save()
            return True
        except (Exception) as error:
            logger.error(f'could not update process: {str(error)}')
            return error
    
    ##############################################
    @staticmethod
    def sendProcess(processID):
        """
        Send process to contractor.

        :param processID: ID of the process that is being sent
        :type processID: str
        :return: Nothing or an error
        :rtype: None or error
        """
        #TODO - create data entries for everything that's happening
        try:
            processObj = Process.objects.get(processID=processID)
            
            contractorObj = Organization.objects.get(hashedID=processObj.processDetails[ProcessDetails.provisionalContractor])
            processObj.contractor = contractorObj
            processObj.save()

            #TODO change Status
            # updateProcess

            return None
        except (Exception) as error:
            logger.error(f'could not send process: {str(error)}')
            return error

    ##############################################
    @staticmethod
    def deleteFromProcess(projectID, processID, updateType: ProcessUpdates, content, deletedBy):
        """
        Delete details of a process like its status, or content. 

        :param projectID: Project that this process belongs to, not needed here
        :type projectID: str
        :param processID: unique process ID to be edited
        :type processID: str
        :param updateType: changed process details
        :type updateType: EnumUpdates
        :param content: deletions
        :type content: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """
        try:
            updated = timezone.now()
            currentProcess = Process.objects.get(processID=processID)
            currentProcess.updatedWhen = updated
            dataID = crypto.generateURLFriendlyRandomString()

            if updateType == ProcessUpdates.messages:
                ProcessManagementBase.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.MESSAGE, "content": content})
                del currentProcess.messages[content]

            elif updateType == ProcessUpdates.files:
                for entry in content:
                    s3.manageLocalS3.deleteFile(content[entry][FileObjectContent.path])
                    ProcessManagementBase.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.FILE, "content": entry})
                    del currentProcess.files[content[entry][FileObjectContent.id]]

            elif updateType == ProcessUpdates.processStatus:
                currentProcess.processStatus = ProcessStatus.DRAFT
                ProcessManagementBase.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.STATUS, "content": ProcessUpdates.processStatus})
                
            elif updateType == ProcessUpdates.processDetails:
                for key in content:
                    del currentProcess.processDetails[key]
                ProcessManagementBase.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.DETAILS, "content": ProcessUpdates.processDetails})

            elif updateType == ProcessUpdates.serviceDetails:
                currentProcess.serviceDetails = serviceManager.getService(currentProcess.serviceType).deleteServiceDetails(currentProcess.serviceDetails, content)
                ProcessManagementBase.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.DETAILS, "content": ProcessUpdates.serviceDetails})

            elif updateType == ProcessUpdates.serviceStatus:
                currentProcess.serviceStatus = 0 #TODO
                ProcessManagementBase.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.STATUS, "content": ProcessUpdates.serviceStatus})

            elif updateType == ProcessUpdates.serviceType:
                currentProcess.serviceType = serviceManager.getNone()
                ProcessManagementBase.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.OTHER, "content": ProcessUpdates.serviceType})

            elif updateType == ProcessUpdates.provisionalContractor:
                currentProcess.processDetails[ProcessDetails.provisionalContractor] = ""
                ProcessManagementBase.createDataEntry({}, dataID, processID, DataType.DELETION, deletedBy, {"deletion": DataType.OTHER, "content": ProcessUpdates.provisionalContractor})

            currentProcess.save()
            return True
        except (Exception) as error:
            logger.error(f'could not delete from process: {str(error)}')
            return error

    ##############################################
    @staticmethod
    def addProcessTemplateToProject(projectID, template, clientID):
        """
        add a process to an existing project in the database

        :param projectID: project ID to retrieve data from
        :type projectID: str
        :param template: Dictionary with templated process
        :type template: Dict
        :return: None or Error
        :rtype: None or Error

        """

        try:
            # check if exists
            projectObj = Project.objects.get(projectID=projectID)
            
            # if it does, create process
            processID = template[ProcessDescription.processID]
            serviceType = template[ProcessDescription.serviceType]
            processStatus = template[ProcessDescription.processStatus]
            serviceStatus = template[ProcessDescription.serviceStatus]
            serviceDetails = template[ProcessDescription.serviceDetails]
            processDetails = template[ProcessDescription.processDetails]
            files = template[ProcessDescription.files]
            messages = template[ProcessDescription.messages]
            client = clientID
            processObj = Process.objects.create(processID=processID, project=projectObj, processDetails=processDetails, processStatus=processStatus, serviceDetails=serviceDetails, serviceStatus=serviceStatus, serviceType=serviceType, client=client, files=files, messages=messages, updatedWhen=timezone.now())
            return None
        except (Exception) as error:
            logger.error(f'could not add process template to project: {str(error)}')
            return error


    ##############################################
    @staticmethod
    def getInfoAboutProjectForWebsocket(projectID, affectedProcessesIDs:list, event):
        """
        Retrieve information about the users connected to the project from the database. 

        :param projectID: project ID to retrieve data from
        :type projectID: str
        :return: Dictionary of users with project ID and processes in order for the websocket to fire events
        :rtype: Dict

        """
        # outputList for events
        dictForEventsAsOutput = {}

        projectObj = Project.objects.get(projectID=projectID)
        dictForEventsAsOutput[projectObj.client] = {EventsDescription.eventType: EventsDescription.projectEvent, EventsDescription.events: []}
        dictForEventsAsOutput[projectObj.client][EventsDescription.events] = [{ProjectDescription.projectID: projectID, SessionContentSemperKI.processes: [] }]
        for process in projectObj.processes.all():
            if process.processID in affectedProcessesIDs:
                if projectObj.client != process.client:
                    if process.client not in dictForEventsAsOutput:
                        dictForEventsAsOutput[process.client] = {EventsDescription.eventType: EventsDescription.projectEvent, EventsDescription.events: []}
                        dictForEventsAsOutput[process.client][EventsDescription.events] = [{ProjectDescription.projectID: projectID, SessionContentSemperKI.processes: [{ProcessDescription.processID: process.processID, event: 1}] }]
                    else:
                        dictForEventsAsOutput[process.client][EventsDescription.events][0][SessionContentSemperKI.processes].append({ProcessDescription.processID: process.processID, event: 1})
                else:
                    dictForEventsAsOutput[projectObj.client][EventsDescription.events][0][SessionContentSemperKI.processes].append({ProcessDescription.processID: process.processID, event: 1})
                
                # only signal contractors that received the process 
                if process.processStatus >= ProcessStatus.REQUESTED:
                    contractorID = ""
                    if process.contractor != None:
                        contractorID = process.contractor.hashedID
                    elif ProcessDetails.provisionalContractor in process.processDetails and process.processDetails[ProcessDetails.provisionalContractor] != "":
                        contractorID = process.processDetails[ProcessDetails.provisionalContractor]
                    
                    if contractorID != "":
                        if projectObj.client != contractorID:
                            if contractorID not in dictForEventsAsOutput:
                                dictForEventsAsOutput[contractorID] = {EventsDescription.eventType: EventsDescription.projectEvent, EventsDescription.events: []}
                                dictForEventsAsOutput[contractorID][EventsDescription.events] = [{ProjectDescription.projectID: projectID, SessionContentSemperKI.processes: [{ProcessDescription.processID: process.processID, event: 1}] }]
                            else:
                                dictForEventsAsOutput[contractorID][EventsDescription.events][0][SessionContentSemperKI.processes].append({ProcessDescription.processID: process.processID, event: 1})
        return dictForEventsAsOutput
    
    ##############################################
    @staticmethod
    def getAllProjectsFlat():
        """
        Return flat list of all projects, for admins

        :return: Json with all projects and their data
        :rtype: List of dicts
        """
        outList = []
        allOCs = Project.objects.all()
        for entry in allOCs:
            currentOC = entry.toDict()
            currentOC["processesCount"] = len(entry.processes.all())
            outList.append(currentOC)

        return outList
    
    ##############################################
    @staticmethod
    def getProcessesPerPID(projectID):
        """
        Retrieve infos about one project, for admins

        :param projectID: project of interest
        :type projectID: str
        :return: list of all processes of that OC
        :rtype: list
        """
        outList = []
        PObject = Project.objects.get(projectID=projectID)
        for entry in PObject.processes.all():
            outList.append(entry.toDict())
        return outList

###############################################################################
    ##############################################
    @staticmethod
    def createProject(projectID:str, client:str):
        """
        Create the project in the database directly

        :param projectID: The ID of the project
        :type projectID: str
        :param client: the userID of the person creating the project
        :type client: str
        :return: Nothing
        :rtype: None
        
        """
        try:
            now = timezone.now()

            defaultProjectObject = ProjectInterface(projectID, str(now))

            projectObj, flag = Project.objects.update_or_create(projectID=projectID, defaults={ProjectDescription.projectStatus: defaultProjectObject.projectStatus, ProjectDescription.updatedWhen: now, ProjectDescription.client: client, ProjectDescription.projectDetails: defaultProjectObject.projectDetails})
            return None
        except (Exception) as error:
            logger.error(f'could not add project to database: {str(error)}')
            return error
    
    ##############################################
    @staticmethod
    def createProcess(projectID:str, processID:str, client:str):
        """
        Create the project in the database directly

        :param projectID: The ID of the project
        :type projectID: str
        :param processID: The ID of the process
        :type processID: str
        :param client: the userID of the person creating the project
        :type client: str
        :return: Nothing
        :rtype: None
        
        """
        try:
            now = timezone.now()

            projectObj = ProcessManagementBase.getProjectObj(projectID)

            defaultProcessObj = ProcessInterface(processID, str(now))

            processObj, flag = Process.objects.update_or_create(processID=processID, defaults={ProcessDescription.project: projectObj, ProcessDescription.serviceType: defaultProcessObj.serviceType, ProcessDescription.serviceStatus: defaultProcessObj.serviceStatus, ProcessDescription.serviceDetails: defaultProcessObj.serviceDetails, ProcessDescription.processDetails: defaultProcessObj.processDetails, ProcessDescription.processStatus: defaultProcessObj.processStatus, ProcessDescription.client: client, ProcessDescription.files: defaultProcessObj.files, ProcessDescription.messages: defaultProcessObj.messages, ProcessDescription.updatedWhen: now})
            ProcessManagementBase.createDataEntry({}, crypto.generateURLFriendlyRandomString(), processID, DataType.CREATION, client)
            
            return None
        except (Exception) as error:
            logger.error(f'could not add project to database: {str(error)}')
            return error
    
    ##############################################
    @staticmethod
    def addProjectToDatabase(session):
        """
        Add project and processes for that user. Check if user already has a project and append if so, create a new process if not.

        :param session: session of user
        :type session: session dict
        :return: Dictionary of users with project id and processes in order for the websocket to fire events
        :rtype: Dict

        """
        now = timezone.now()
        try:
            # Check if there's anything to save
            if SessionContentSemperKI.CURRENT_PROJECTS not in session:
                return None
            
            # first get user
            clientID = profileManagement[session[SessionContent.PG_PROFILE_CLASS]].getClientID(session)

            # then go through projects
            for projectID in session[SessionContentSemperKI.CURRENT_PROJECTS]:

                # project object
                # check if obj already exists in database and overwrite it
                # if not, create a new entry
                existingObj = session[SessionContentSemperKI.CURRENT_PROJECTS][projectID]

                projectObj, flag = Project.objects.update_or_create(projectID=projectID, defaults={ProjectDescription.projectStatus: existingObj[ProjectDescription.projectStatus], ProjectDescription.updatedWhen: now, ProjectDescription.client: clientID, ProjectDescription.projectDetails: existingObj[ProjectDescription.projectDetails]})
                # save processes
                for entry in session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes]:
                    process = session[SessionContentSemperKI.CURRENT_PROJECTS][projectID][SessionContentSemperKI.processes][entry]
                    processID = process[ProcessDescription.processID]
                    serviceType = process[ProcessDescription.serviceType]
                    serviceStatus = process[ProcessDescription.serviceStatus]
                    serviceDetails = process[ProcessDescription.serviceDetails]
                    processStatus = process[ProcessDescription.processStatus]
                    processDetails = process[ProcessDescription.processDetails]
                    files = process[ProcessDescription.files]
                    messages = process[ProcessDescription.messages]

                    processObj, flag = Process.objects.update_or_create(processID=processID, defaults={ProcessDescription.project:projectObj, ProcessDescription.serviceType: serviceType, ProcessDescription.serviceStatus: serviceStatus, ProcessDescription.serviceDetails: serviceDetails, ProcessDescription.processDetails: processDetails, ProcessDescription.processStatus: processStatus, ProcessDescription.client: clientID, ProcessDescription.files: files, ProcessDescription.messages: messages, ProcessDescription.updatedWhen: now})
                    ProcessManagementBase.createDataEntry({}, crypto.generateURLFriendlyRandomString(), processID, DataType.CREATION, clientID)

                    # generate entries in data
                    for elem in process[ProcessDescription.files]:
                        fileEntry = process[ProcessDescription.files][elem]
                        if fileEntry[FileObjectContent.createdBy] == GlobalDefaults.anonymous:
                            fileEntry[FileObjectContent.createdBy] = clientID
                        dataID = crypto.generateURLFriendlyRandomString()
                        ProcessManagementBase.createDataEntry(fileEntry, dataID, processID, DataType.FILE, fileEntry[FileObjectContent.createdBy], {}, elem)

            return None
        except (Exception) as error:
            logger.error(f'could not add project to database: {str(error)}')
            return error

    ##############################################
    @staticmethod
    def getProjects(session):
        """
        Get all processes for that user.

        :param session: session of that user
        :type session: dict
        :return: sorted list with all processes
        :rtype: list

        """
        try:
            # get associated projects
            currentClient = profileManagement[session[SessionContent.PG_PROFILE_CLASS]].getClientID(session)
            projects = Project.objects.filter(client=currentClient)
            
            output = []
            
            for project in projects:
                currentProject = project.toDict()
                processesOfThatProject = []
                for entry in project.processes.all():
                    currentProcess = entry.toDict()
                    processesOfThatProject.append(currentProcess)
                currentProject[SessionContentSemperKI.processes] = processesOfThatProject
                output.append(currentProject)

            if ProfileManagementBase.checkIfUserIsInOrganization(session):
                # Code specific for orgas
                # Add projects where the organization is registered as contractor
                organizationObj = ProfileManagementBase.getOrganizationObject(session)
                receivedProjects = {}
                for processAsContractor in organizationObj.asContractor.all():
                    project = processAsContractor.project

                    if project.projectID not in receivedProjects:
                        receivedProjects[project.projectID] = project.toDict()
                        receivedProjects[project.projectID][SessionContentSemperKI.processes] = []

                    receivedProjects[project.projectID][SessionContentSemperKI.processes].append(processAsContractor.toDict())
                
                for project in receivedProjects:
                    output.append(receivedProjects[project])

            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x[ProjectDescription.createdWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output

        except (Exception) as error:
            logger.error(f'could not get projects: {str(error)}')
        
        return []
    
    ##############################################
    @staticmethod
    def getProjectsFlat(session):
        """
        Get all projects for that user but with limited detail.

        :param session: session of that user
        :type session: dict
        :return: sorted list with projects
        :rtype: list

        """
        try:
            # get user
            currentClient = profileManagement[session[SessionContent.PG_PROFILE_CLASS]].getClientID(session)
            projects = Project.objects.filter(client=currentClient)
            # get associated projects
            output = []
            
            for project in projects:
                if SessionContentSemperKI.CURRENT_PROJECTS in session:
                    if project.projectID in session[SessionContentSemperKI.CURRENT_PROJECTS]:
                        continue
                currentProject = project.toDict()
                currentProject["processesCount"] = len(project.processes.all())
                currentProject["owner"] = True
                    
                output.append(currentProject)
            
            if ProfileManagementBase.checkIfUserIsInOrganization(session):
                # Code specific for orgas
                # Add projects where the organization is registered as contractor
                organizationObj = Organization.objects.get(hashedID=ProfileManagementBase.getOrganizationHashID(session))
                receivedProjects = {}
                for processAsContractor in organizationObj.asContractor.all():
                    project = processAsContractor.project

                    if project.projectID not in receivedProjects:
                        receivedProjects[project.projectID] = project.toDict()
                        receivedProjects[project.projectID]["processesCount"] = 0

                    receivedProjects[project.projectID]["processesCount"] += 1
                
                for project in receivedProjects:
                    receivedProjects[project]["owner"] = False
                    output.append(receivedProjects[project])
            
            
            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x[ProjectDescription.createdWhen], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output

        except (Exception) as error:
            logger.error(f'could not get projects flat: {str(error)}')
        
        return []
    
    ##############################################
    @staticmethod
    def getAllContractors(selectedService:int):
        """
        Get all contractors.
        
        :return: All contractors
        :rtype: Dictionary

        """
        try:
            listOfSuitableContractors = Organization.objects.filter(supportedServices__contains=[selectedService])
            returnValue = []
            for entry in listOfSuitableContractors:
                detailsOfOrganization = {}
                if OrganizationDetails.adress in entry.details:
                    detailsOfOrganization[OrganizationDetails.adress] = entry.details[OrganizationDetails.adress]
                returnValue.append({OrganizationDescription.hashedID: entry.hashedID, OrganizationDescription.name: entry.name, OrganizationDescription.details: detailsOfOrganization})
        except (Exception) as error:
            logger.error(f"Error getting all contractors: {str(error)}")

        return returnValue