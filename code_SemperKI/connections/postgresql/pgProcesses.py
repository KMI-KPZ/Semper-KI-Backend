"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls
"""
import enum

from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from code_General.utilities import basics

from code_General.modelFiles.userModel import User
from code_General.modelFiles.organizationModel import Organization
from code_General.connections.postgresql.pgProfiles import ProfileManagementBase
from ...modelFiles.projectModel import Project
from ...modelFiles.processModel import Process
from ...modelFiles.dataModel import Data

from code_General.connections import s3
from code_General.utilities import crypto

from code_General.definitions import FileObjectContent, OrganizationDescription
from ...definitions import *

from ...services import serviceManager 

import logging
logger = logging.getLogger("django_debug")

#TODO: switch to async versions at some point



####################################################################################
# Projects/Processes general
class ProcessManagementBase():
    
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
    def getProject(projectID, currentUserHashID, currentOrgaHashID):
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
            showProjectDetails = True if projectObj.client == currentUserHashID else False # make sure nobody else sees this

            processesOfThatProject = []
            for entry in projectObj.processes.all():
                if entry.client == currentUserHashID or (currentOrgaHashID != "" and currentOrgaHashID == entry.contractor.hashedID): 
                    processesOfThatProject.append(entry.toDict())
                    showProjectDetails = True
            output[SessionContentSemperKI.processes] = processesOfThatProject
            
            if showProjectDetails:
                return output

        except (Exception) as error:
            logger.error(f'could not get project: {str(error)}')
        
        return {}
    

    ##############################################
    @staticmethod
    def getAllUsersOfProcess(processID):
        """
        Get all users that are connected to that processID.

        :param processID: unique process ID
        :type processID: str
        :return: List of all userIDs
        :rtype: List

        """
        try:
            currentProcess = Process.objects.get(processID=processID)

            users = list(User.objects.filter(hashedID=currentProcess.client).all())
            users.extend(list(Organization.objects.filter(hashedID=currentProcess.client).all()))
            users.extend([currentProcess.contractor])
            return users
        except (Exception) as error:
            logger.error(f'could not get all users of process: {str(error)}')
        return []
    
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

            allFiles = ProcessManagementBase.getDataByType(DataType.FILE, processID, processObj)
            # delete files as well
            for entry in allFiles:
                s3.manageLocalS3.deleteFile(entry[FileObjectContent.path])
            
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
            if updateType == ProjectUpdates.status:
                currentProject = Project.objects.get(projectID=projectID)
                currentProject.status = content
                currentProject.updatedWhen = updated
                currentProject.save()

            elif updateType == ProjectUpdates.details:
                currentProject = Project.objects.get(projectID=projectID)
                for key in content:
                    currentProject.details[key] = content[key]
                currentProject.updatedWhen = updated
                currentProject.save()
            return True
        except (Exception) as error:
            logger.error(f'could not update project: {str(error)}')
            return error
    
    ##############################################
    @staticmethod
    def updateProcess(processID, updateType: ProcessUpdates, content, updatedBy):
        """
        Change details of a process like its status, or save communication. 

        :param processID: unique processID to be edited
        :type processID: str
        :param updateType: changed process details
        :type updateType: EnumUpdates
        :param content: changed process, can be many stuff
        :type content: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """
        # TODO - create data entries for everything that's happening
        updated = timezone.now()
        try:
            currentProcess = Process.objects.get(processID=processID)
            currentProcess.updatedWhen = updated

            if updateType == ProcessUpdates.messages:
                dataID = crypto.generateURLFriendlyRandomString()
                ProcessManagementBase.createDataEntry(content, dataID, processID, DataType.MESSAGE, updatedBy)
                currentProcess.messages[content] = dataID

            elif updateType == ProcessUpdates.files:
                for entry in content:
                    dataID = crypto.generateURLFriendlyRandomString()
                    ProcessManagementBase.createDataEntry(content[entry], dataID, processID, DataType.FILE, updatedBy, {}, content[entry][FileObjectContent.id])
                    currentProcess.files[content[entry][FileObjectContent.id]] = dataID

            elif updateType == ProcessUpdates.processStatus:
                currentProcess.processStatus = content
                
            elif updateType == ProcessUpdates.processDetails:
                for entry in content:
                    currentProcess.processDetails[entry] = content[entry]

            elif updateType == ProcessUpdates.serviceType:
                currentProcess.serviceType = content
                      
            elif updateType == ProcessUpdates.serviceStatus:
                currentProcess.serviceStatus = content

            elif updateType == ProcessUpdates.serviceDetails:
                currentProcess.serviceDetails = serviceManager.getService(currentProcess.serviceType).updateServiceDetails(currentProcess.serviceDetails, content)

            elif updateType == ProcessUpdates.provisionalContractor:
                currentProcess.processDetails[ProcessDetails.provisionalContractor] = content

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

            return None
        except (Exception) as error:
            logger.error(f'could not send process: {str(error)}')
            return error

    ##############################################
    @staticmethod
    def deleteFromProcess(processID, updateType: ProcessUpdates, content, deletedBy):
        """
        Delete details of a process like its status, or content. 

        :param processID: unique process ID to be edited
        :type processID: str
        :param updateType: changed process details
        :type updateType: EnumUpdates
        :param content: deletions
        :type content: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """
        #TODO - create data entries for everything that's happening
        updated = timezone.now()
        try:
            currentProcess = Process.objects.get(processID=processID)
            currentProcess.updatedWhen = updated

            if updateType == ProcessUpdates.messages:
                ProcessManagementBase.createDataEntry({},crypto.generateURLFriendlyRandomString(), processID, DataType.DELETION, deletedBy, {"deletion": DataType.MESSAGE, "content": content})
                del currentProcess.messages[content]

            elif updateType == ProcessUpdates.files:
                for entry in content:
                    s3.manageLocalS3.deleteFile(content[entry][FileObjectContent.path])
                    ProcessManagementBase.createDataEntry({},crypto.generateURLFriendlyRandomString(), processID, DataType.DELETION, deletedBy, {"deletion": DataType.FILE, "content": entry})
                    del currentProcess.files[content[entry][FileObjectContent.id]]

            elif updateType == ProcessUpdates.processStatus:
                currentProcess.processStatus = ProcessStatus.DRAFT
                
            elif updateType == ProcessUpdates.processDetails:
                for key in content:
                    del currentProcess.processDetails[key]

            elif updateType == ProcessUpdates.serviceDetails:
                currentProcess.serviceDetails = serviceManager.getService(currentProcess.serviceType).deleteServiceDetails(currentProcess.serviceDetails, content)

            elif updateType == ProcessUpdates.serviceStatus:
                currentProcess.serviceStatus = 0 #TODO

            elif updateType == ProcessUpdates.serviceType:
                currentProcess.serviceType = serviceManager.getNone()

            elif updateType == ProcessUpdates.provisionalContractor:
                currentProcess.processDetails[ProcessDetails.provisionalContractor] = ""

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
        dictForEventsAsOutput[projectObj.client] = {"eventType": "projectEvent"}
        dictForEventsAsOutput[projectObj.client]["processes"] = []
        dictForEventsAsOutput[projectObj.client]["projectID"] = projectID
        for process in projectObj.processes.all():
            if process.processID in affectedProcessesIDs:
                if projectObj.client != process.client:
                    if process.client not in dictForEventsAsOutput:
                        dictForEventsAsOutput[process.client] = {"eventType": "projectEvent"}
                        dictForEventsAsOutput[process.client]["process"] = [{"processID": process.processID, event: 1}]
                        dictForEventsAsOutput[process.client]["projectID"] = projectID
                    else:
                        dictForEventsAsOutput[process.client]["processes"].append({"processID": process.processID, event: 1})
                else:
                    dictForEventsAsOutput[projectObj.client]["processes"].append({"processID": process.processID, event: 1})
                
                # only signal contractors that received the process 
                if process.processStatus >= ProcessStatus.REQUESTED:
                    contractorID = process.contractor.hashedID
                    if projectObj.client != contractorID:
                        if contractorID not in dictForEventsAsOutput:
                            dictForEventsAsOutput[contractorID] = {"eventType": "projectEvent"}
                            dictForEventsAsOutput[contractorID]["processes"] = [{"processID": process.processID, event: 1}]
                            dictForEventsAsOutput[contractorID]["projectID"] = projectID
                        else:
                            dictForEventsAsOutput[contractorID]["processes"].append({"processID": process.processID, event: 1})

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


    ####################################################################################
    # Processes/Projects from User
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
        # TODO for all files & messages: generate data and message entries and refill "files" and "messages" to link to that ID
        now = timezone.now()
        try:
            # first get user
            clientID = ProfileManagementBase.getUserHashID(session)

            # then go through projects
            for projectID in session[SessionContentSemperKI.CURRENT_PROJECTS]:

                # project object
                # check if obj already exists in database and overwrite it
                # if not, create a new entry
                existingObj = session[SessionContentSemperKI.CURRENT_PROJECTS][projectID]

                projectObj, flag = Project.objects.update_or_create(projectID=projectID, defaults={ProjectDescription.status: existingObj[ProjectDescription.status], ProjectDescription.updatedWhen: now, ProjectDescription.client: clientID, ProjectDescription.details: existingObj[ProjectDescription.details]})
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
            projects = Project.objects.filter(client=ProfileManagementBase.getUserHashID(session))
            
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
                organizationObj = Organization.objects.get(hashedID=ProfileManagementBase.getOrgaHashID(session))
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
            projects = Project.objects.filter(client=ProfileManagementBase.getUserHashID(session))
            # get associated projects
            output = []
            
            for project in projects:
                if SessionContentSemperKI.CURRENT_PROJECTS in session:
                    if project.projectID in session[SessionContentSemperKI.CURRENT_PROJECTS]:
                        continue
                currentProject = project.toDict()
                currentProject["processesCount"] = len(project.processes.all())
                    
                output.append(currentProject)
            
            if ProfileManagementBase.checkIfUserIsInOrganization(session):
                # Code specific for orgas
                # Add projects where the organization is registered as contractor
                organizationObj = Organization.objects.get(hashedID=ProfileManagementBase.getOrgaHashID(session))
                receivedProjects = {}
                for processAsContractor in organizationObj.asContractor.all():
                    project = processAsContractor.project

                    if project.projectID not in receivedProjects:
                        receivedProjects[project.projectID] = project.toDict()
                        receivedProjects[project.projectID]["processesCount"] = 0

                    receivedProjects[project.projectID]["processesCount"] += 1
                
                for project in receivedProjects:
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
                returnValue.append({OrganizationDescription.hashedID: entry.hashedID, OrganizationDescription.name: entry.name, OrganizationDescription.details: entry.details})
        except (Exception) as error:
            logger.error(f"Error getting all contractors: {str(error)}")

        return returnValue