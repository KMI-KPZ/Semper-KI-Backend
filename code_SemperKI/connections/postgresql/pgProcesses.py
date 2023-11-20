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
from ...modelFiles.projectModel import Project
from ...modelFiles.processModel import Process
from ...modelFiles.dataModel import Data

from code_General.connections import s3
from code_General.utilities import crypto

from ...definitions import DataType, ProcessStatus, FileObject, ProcessUpdates, ProcessDetails

from ...services import services, ServiceTypes, ServicesDictionaryStructure

import logging
logger = logging.getLogger("django_debug")

#TODO: switch to async versions at some point



####################################################################################
# Projects/Processes general
class ProcessManagementBase():
    
    ##############################################
    @staticmethod
    def getData(processID):
        """
        Get all files.

        :param processID: process ID for a process
        :type processID: str
        :return: list of all data
        :rtype: list
        
        """

        try:
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
    def getDataWithID(processID, IDofData):
        """
        Get one file in particular.

        :param processID: process ID for a process
        :type processID: str
        :param IDofData: ID for a datum
        :type IDofData: str
        :return: this datum
        :rtype: dict
        
        """

        try:
            processObj = Process.objects.filter(processID=processID)
            date = processObj.data.filter(contentID=IDofData)
            return date.toDict()
        except (Exception) as error:
            logger.error(f'Generic error in getDataWithID: {str(error)}')

        return {}
    
    ##############################################
    @staticmethod
    def getDataByType(processID, typeOfData:DataType):
        """
        Get one file in particular.

        :param processID: process ID for a process
        :type processID: str
        :param typeOfData: type of this data
        :type typeOfData: DataType
        :return: all results
        :rtype: list
        
        """

        try:
            processObj = Process.objects.filter(processID=processID)
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
    def createDataEntry(data, dataID, processID, typeOfData:DataType, createdBy, details={}, IDofData=""):
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
            showProjectDetails = False # make sure nobody else sees this

            processesOfThatProject = []
            for entry in projectObj.processes.all():
                if entry.client == currentUserHashID or (currentOrgaHashID != "" and currentOrgaHashID == entry.contractor.hashedID): 
                    processesOfThatProject.append(entry.toDict())
                    showProjectDetails = True
            output["processes"] = processesOfThatProject
            
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

            allFiles = ProcessManagementBase.getDataByType(processID, DataType.FILE)
            # delete files as well
            for entry in allFiles:
                s3.manageLocalS3.deleteFile(entry["id"])
            
            # if that was the last process, delete the project as well
            # if len(currentProcess.project.processes.all()) == 1:
            #     currentProcess.project.delete()
            # else:
            currentProcess.project.updatedWhen = updated
            currentProcess.delete()
            currentProcess.save()
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
            currentProject.save()
            return True
        except (ObjectDoesNotExist) as error:
            return None
        except (Exception) as error:
            logger.error(f'could not delete project: {str(error)}')
        return False

    ##############################################
    @staticmethod
    def updateProject(projectID, updateType: ProcessUpdates, content):
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
            if updateType == ProcessUpdates.STATUS:
                currentProject = Project.objects.get(projectID=projectID)
                currentProject.status = content
                currentProject.updatedWhen = updated
                currentProject.save()

            elif updateType == ProcessUpdates.DETAILS:
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
        # TODO
        updated = timezone.now()
        try:
            currentProcess = Process.objects.get(processID=processID)
            currentProcess.updatedWhen = updated

            if updateType == ProcessUpdates.MESSAGES:
                ProcessManagementBase.createDataEntry(content, crypto.generateURLFriendlyRandomString(), processID, DataType.MESSAGE, updatedBy)
            
            elif updateType == ProcessUpdates.STATUS:
                currentProcess.processStatus = content
                
            elif updateType == ProcessUpdates.FILES:
                for entry in content:
                    ProcessManagementBase.createDataEntry(content[entry], crypto.generateURLFriendlyRandomString(), processID, DataType.FILE, updatedBy, {}, content[entry]["id"])
                
            elif updateType == ProcessUpdates.SERVICE_TYPE:
                # TODO
                if content == ServiceTypes.ADDITIVE_MANUFACTURING:
                    currentProcess.serviceType = ServiceTypes.ADDITIVE_MANUFACTURING
                elif content == ServiceTypes.CREATE_MODEL:
                    currentProcess.serviceType = ServiceTypes.CREATE_MODEL
            
            elif updateType == ProcessUpdates.SERVICE:
                currentProcess.serviceDetails = services[currentProcess.serviceType][ServicesDictionaryStructure.CONNECTIONS].updateServiceDetails(currentProcess.serviceDetails, content)

            elif updateType == ProcessUpdates.CONTRACTOR:
                currentProcess.processDetails[ProcessDetails.PROVISIONAL_CONTRACTOR] = content

            elif updateType == ProcessUpdates.DETAILS:
                for entry in content:
                    currentProcess.processDetails[entry] = content[entry]

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
        # TODO
        try:
            processObj = Process.objects.get(processID=processID)
            
            contractorObj = Organization.objects.get(hashedID=processObj.processDetails[ProcessDetails.PROVISIONAL_CONTRACTOR])
            processObj.contractor = contractorObj

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
        #TODO
        updated = timezone.now()
        try:
            currentProcess = Process.objects.get(processID=processID)
            currentProcess.updatedWhen = updated

            if updateType == ProcessUpdates.MESSAGES:
                ProcessManagementBase.createDataEntry({},crypto.generateURLFriendlyRandomString(), processID, DataType.DELETION, deletedBy, {"deletion": DataType.MESSAGE, "content": content})
            
            elif updateType == ProcessUpdates.STATUS:
                currentProcess.processStatus = ProcessStatus.DRAFT
                
            elif updateType == ProcessUpdates.FILES:
                for entry in content:
                    s3.manageLocalS3.deleteFile(entry["id"])
                    ProcessManagementBase.createDataEntry({},crypto.generateURLFriendlyRandomString(), processID, DataType.DELETION, deletedBy, {"deletion": DataType.FILE, "content": entry})
                
            elif updateType == ProcessUpdates.SERVICE:
                currentProcess.serviceDetails = services[currentProcess.serviceType][ServicesDictionaryStructure.CONNECTIONS].deleteServiceDetails(currentProcess.serviceDetails, content)

            elif updateType == ProcessUpdates.CONTRACTOR:
                currentProcess.processDetails[ProcessDetails.PROVISIONAL_CONTRACTOR] = ""

            elif updateType == ProcessUpdates.DETAILS:
                for key in content:
                    del currentProcess.processDetails[key]

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
            selectedContractor = template["contractor"]
            processID = template["processID"]
            service = template["service"]
            status = template["status"]
            serviceStatus = template["serviceStatus"]
            messages = template["messages"]
            files = template["files"]
            details = template["details"]
            processObj = Process.objects.create(processID=processID, project=projectObj, service=service, status=status, serviceStatus=serviceStatus, messages=messages, details=details, files=files, client=clientID, contractor=selectedContractor, updatedWhen=timezone.now())
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
                if process.status >= basics.ProcessStatus.getStatusCodeFor("REQUESTED"):
                    for contractor in process.contractor:
                        if projectObj.client != contractor:
                            if contractor not in dictForEventsAsOutput:
                                dictForEventsAsOutput[contractor] = {"eventType": "projectEvent"}
                                dictForEventsAsOutput[contractor]["processes"] = [{"processID": process.processID, event: 1}]
                                dictForEventsAsOutput[contractor]["projectID"] = projectID
                            else:
                                dictForEventsAsOutput[contractor]["processes"].append({"processID": process.processID, event: 1})

        return dictForEventsAsOutput
    
    ##############################################
    @staticmethod
    def getAllPsFlat():
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
class ProcessManagementUser(ProcessManagementBase):
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
            # first get user
            client = User.objects.get(subID=session["user"]["userinfo"]["sub"])

            # then go through projects
            for projectID in session["currentProjects"]:

                # project object
                # check if obj already exists in database and overwrite it
                # if not, create a new entry
                existingObj = session["currentProjects"][projectID]

                projectObj, flag = Project.objects.update_or_create(projectID=projectID, defaults={"status": existingObj["status"], "updatedWhen": now, "client": client.hashedID, "details": existingObj["details"]})
                # retrieve files
                # uploadedFiles = []
                # (contentOrError, Flag) = redis.retrieveContent(session.session_key)
                # if Flag:
                #     for entry in contentOrError:
                #         uploadedFiles.append({"filename":entry[1], "path": session.session_key})

                # save processes
                for entry in session["currentProjects"][projectID]["processes"]:
                    process = session["currentProjects"][projectID]["processes"][entry]
                    selectedContractor = process["contractor"]
                    processID = process["processID"]
                    service = process["service"]
                    status = process["status"]
                    serviceStatus = process["serviceStatus"]
                    messages = process["messages"]
                    files = process["files"]
                    details = process["details"]
                    processObj, flag = Process.objects.update_or_create(processID=processID, defaults={"project":projectObj, "service": service, "status": status, "messages": messages, "serviceStatus": serviceStatus, "details": details, "files": files, "client": client.hashedID, "contractor": selectedContractor, "updatedWhen": now})
                    
                    # for contractor in selectedContractor:
                    #     contractorObj = Organization.objects.get(hashedID=contractor)
                    #     contractorObj.processesReceived.add(processObj)
                    #     contractorObj.save()
                    
                # link project to client
                client.projects.add(projectObj)
                client.save()

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
            # get user
            currentUser = User.objects.get(subID=session["user"]["userinfo"]["sub"])
            projects = currentUser.projects.all()
            # get associated projects
            output = []
            
            for project in projects:
                currentProject = {}
                currentProject["projectID"] = project.projectID
                currentProject["created"] = str(project.createdWhen)
                currentProject["updated"] = str(project.updatedWhen)
                currentProject["client"] = project.client
                currentProject["status"] = project.status
                currentProject["details"] = project.details
                processesOfThatProject = []
                for entry in project.processes.all():
                    currentProcess = {}
                    currentProcess["client"] = entry.client
                    currentProcess["processID"] = entry.processID
                    currentProcess["contractor"] = entry.contractor
                    currentProcess["service"] = entry.service
                    currentProcess["status"] = entry.status
                    currentProcess["serviceStatus"] = entry.serviceStatus
                    currentProcess["created"] = str(entry.createdWhen)
                    currentProcess["updated"] = str(entry.updatedWhen)
                    currentProcess["messages"] = entry.messages
                    currentProcess["details"] = entry.details
                    currentProcess["files"] = entry.files
                    processesOfThatProject.append(currentProcess)
                currentProject["processes"] = processesOfThatProject
                output.append(currentProject)
            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["created"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
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
            currentUser = User.objects.get(subID=session["user"]["userinfo"]["sub"])
            projects = currentUser.projects.all()
            # get associated projects
            output = []
            
            for project in projects:
                if "currentProjects" in session:
                    if project.projectID in session["currentProjects"]:
                        continue
                currentProject = {}
                currentProject["projectID"] = project.projectID
                currentProject["created"] = str(project.createdWhen)
                currentProject["updated"] = str(project.updatedWhen)
                currentProject["status"] = project.status
                currentProject["client"] = project.client
                currentProject["details"] = project.details
                currentProject["processesCount"] = len(project.processes.all())
                    
                output.append(currentProject)
            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["created"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output

        except (Exception) as error:
            logger.error(f'could not get projects flat: {str(error)}')
        
        return []

####################################################################################
# Projects and processes from and for Organizations
class ProcessManagementOrganization(ProcessManagementBase):

    ##############################################
    @staticmethod
    def addProjectToDatabase(session):
        """
        Add project and processes to database for that organization. 

        :param session: session of user
        :type session: session dict
        :return: None
        :rtype: None or Exception

        """
        now = timezone.now()
        try:

            # first get organization
            client = Organization.objects.get(subID=session["user"]["userinfo"]["org_id"])

            # then go through projects
            for projectID in session["currentProjects"]:

                # project object
                existingObj = session["currentProjects"][projectID]
                projectObj, flag = Project.objects.update_or_create(projectID=projectID, defaults={"status": existingObj["status"], "updatedWhen": now, "client": client.hashedID, "details": existingObj["details"]})
                # retrieve files
                # uploadedFiles = []
                # (contentOrError, Flag) = redis.retrieveContent(session.session_key)
                # if Flag:
                #     for entry in contentOrError:
                #         uploadedFiles.append({"filename":entry[1], "path": session.session_key})

                # save processes
                for entry in session["currentProjects"][projectID]["processes"]:
                    process = session["currentProjects"][projectID]["processes"][entry]
                    selectedContractor = process["contractor"]
                    processID = process["processID"]
                    service = process["service"]
                    status = process["status"]
                    serviceStatus = process["serviceStatus"]
                    messages = process["messages"]
                    files = process["files"]
                    details = process["details"]
                    processObj, flag = Process.objects.update_or_create(processID=processID, defaults={"project": projectObj, "service": service, "status": status, "serviceStatus": serviceStatus, "messages": messages, "details": details, "files": files, "client": client.hashedID, "contractor": selectedContractor, "updatedWhen": now})

                    # for contractor in selectedManufacturer:
                    #     contractorObj = Organization.objects.get(hashedID=contractor)
                    #     contractorObj.processesReceived.add(processObj)
                    #     contractorObj.save()
            
                # link project to client
                client.projectsSubmitted.add(projectObj)
                client.save()

            return None
        except (Exception) as error:
            logger.error(f'could not add project to database: {str(error)}')
            return error

    ##############################################
    @staticmethod
    def getProjects(session):
        """
        Get all processes for that organization.

        :param session: session of that user
        :type session: dict
        :return: list of processes
        :rtype: list

        """
        try:
            # get organization
            currentUser = Organization.objects.get(subID=session["user"]["userinfo"]["org_id"])
            projects = currentUser.projectsSubmitted.all()

            # get associated projects for submitted processes
            output = []
            
            for project in projects:
                currentProject = {}
                currentProject["projectID"] = project.projectID
                currentProject["created"] = str(project.createdWhen)
                currentProject["updated"] = str(project.updatedWhen)
                currentProject["status"] = project.status
                currentProject["client"] = project.client
                currentProject["details"] = project.details
                processesOfThatProject = []
                for entry in project.processes.all():
                    currentProcess = {}
                    currentProcess["processID"] = entry.processID
                    currentProcess["contractor"] = entry.contractor
                    currentProcess["client"] = entry.client
                    currentProcess["service"] = entry.service
                    currentProcess["status"] = entry.status
                    currentProcess["serviceStatus"] = entry.serviceStatus
                    currentProcess["created"] = str(entry.createdWhen)
                    currentProcess["updated"] = str(entry.updatedWhen)
                    currentProcess["messages"] = entry.messages
                    currentProcess["details"] = entry.details
                    currentProcess["files"] = entry.files
                    processesOfThatProject.append(currentProcess)
                currentProject["processes"] = processesOfThatProject
                output.append(currentProject)

            # get received processes
            receivedProcesses = currentUser.processesReceived.all()
            # since multiple processes could have been received within the same project, we need to collect those
            receivedProjects = {}
            for processEntry in receivedProcesses:
                project = processEntry.project

                if project.projectID not in receivedProjects:
                    receivedProjects[project.projectID] = {"projectID": project.projectID, "client": project.client, "created": str(project.createdWhen), "updated": str(project.updatedWhen), "status": project.status, "processes": []}

                currentProcess = {}
                currentProcess["processID"] = processEntry.processID
                currentProcess["contractor"] = processEntry.contractor
                currentProcess["client"] = processEntry.client
                currentProcess["service"] = processEntry.service
                currentProcess["status"] = processEntry.status
                currentProcess["serviceStatus"] = processEntry.serviceStatus
                currentProcess["created"] = str(processEntry.createdWhen)
                currentProcess["updated"] = str(processEntry.updatedWhen)
                currentProcess["messages"] = processEntry.messages
                currentProcess["details"] = processEntry.details
                currentProcess["files"] = processEntry.files

                receivedProjects[project.projectID]["processes"].append(currentProcess)
            
            # after collection the projects and their processes, we need to add them to the output
            for project in receivedProjects:
                output.append(receivedProjects[project])


            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["created"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output

        except (Exception) as error:
            logger.error(f'could not get projects: {str(error)}')
        
        return []
    
    ##############################################
    @staticmethod
    def getProjectsFlat(session):
        """
        Get all projects for that organization with little information.

        :param session: session of that user
        :type session: dict
        :return: sorted list 
        :rtype: list

        """
        try:
            # get organization
            currentUser = Organization.objects.get(subID=session["user"]["userinfo"]["org_id"])
            projects = currentUser.projectsSubmitted.all()

            # get associated projects for submitted processes
            output = []
            
            for project in projects:
                if "currentProjects" in session:
                    if project.projectID in session["currentProjects"]:
                        continue
                currentProject = {}
                currentProject["projectID"] = project.projectID
                currentProject["created"] = str(project.createdWhen)
                currentProject["updated"] = str(project.updatedWhen)
                currentProject["status"] = project.status
                currentProject["client"] = project.client
                currentProject["details"] = project.details
                currentProject["processesCount"] = len(list(project.processes.all()))

                output.append(currentProject)

            # get received processes
            receivedProcesses = currentUser.processesReceived.all()
            # since multiple processes could have been received within the same project, we need to collect those
            receivedProjects = {}
            for processEntry in receivedProcesses:
                project = processEntry.project

                if project.projectID not in receivedProjects:
                    receivedProjects[project.projectID] = {"projectID": project.projectID, "client": project.client, "created": str(project.createdWhen), "updated": str(project.updatedWhen), "details": project.details, "status": project.status, "processesCount": 0}
                receivedProjects[project.projectID]["processesCount"] += 1
            
            # after collection the projects and their processes, we need to add them to the output
            for project in receivedProjects:
                currentProject = {}
                currentProject["projectID"] = receivedProjects[project]["projectID"]
                currentProject["created"] = receivedProjects[project]["created"]
                currentProject["updated"] = receivedProjects[project]["updated"]
                currentProject["status"] = receivedProjects[project]["status"]
                currentProject["client"] = receivedProjects[project]["client"]
                currentProject["details"] = receivedProjects[project]["details"]
                currentProject["processesCount"] = receivedProjects[project]["processesCount"]

                output.append(currentProject)


            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["created"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output

        except (Exception) as error:
            logger.error(f'could not get projects: {str(error)}')
        
        return []
    
processManagement= {"user": ProcessManagementUser(), "organization": ProcessManagementOrganization()}
