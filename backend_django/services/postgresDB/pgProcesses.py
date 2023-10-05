"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls
"""
import enum

from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from backend_django.utilities import crypto

from ...modelFiles.profileModel import User, Organization
from ...modelFiles.projectModels import Process, Project

from backend_django.services import redis

#TODO: switch to async versions at some point

####################################################################################
# Enum for updateOrder
class EnumUpdates(enum.Enum):
    status = 1
    chat = 2
    files = 3
    service = 4
    contractor = 5
    details = 6

####################################################################################
# Orders general
class ProcessManagementBase():
    
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
            print(error)
        
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
            print(error)
        
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
            # get project
            projectObj = Project.objects.get(projectID=projectID)

            output = {}
            
            output["projectID"] = projectObj.projectID
            output["created"] = str(projectObj.createdWhen)
            output["updated"] = str(projectObj.updatedWhen)
            output["client"] = projectObj.client
            output["state"] = projectObj.status
            output["details"] = projectObj.details

            processesOfThatProject = []
            for entry in projectObj.orders.all():
                currentProcess = {}
                currentProcess["client"] = entry.client
                currentProcess["processID"] = entry.processID
                currentProcess["contractor"] = entry.contractor
                currentProcess["service"] = entry.service
                currentProcess["serviceState"] = entry.serviceState
                currentProcess["state"] = entry.status
                currentProcess["created"] = str(entry.createdWhen)
                currentProcess["updated"] = str(entry.updatedWhen)
                currentProcess["messages"] = entry.messages
                currentProcess["details"] = entry.details
                currentProcess["files"] = entry.files
                processesOfThatProject.append(currentProcess)
            output["processes"] = processesOfThatProject
            
            return output

        except (Exception) as error:
            print(error)
        
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
            users.extend(list(Organization.objects.filter(hashedID=currentProcess.contractor).all()))
            return users
        except (Exception) as error:
            print(error)
        return []

    ##############################################
    @staticmethod
    def deleteProcess(processID):
        """
        Delete specific process.

        :param processID: unique process ID to be deleted
        :type processID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            currentProcess = Process.objects.get(processID=processID)
            if len(currentProcess.projectKey.processes.all()) == 1:
                currentProcess.projectKey.delete()
            else:
                currentProcess.projectKey.updatedWhen = updated
                currentProcess.delete()
            return True
        except (ObjectDoesNotExist) as error:
            return None
        except (Exception) as error:
            print(error)
        return False
    
    ##############################################
    @staticmethod
    def deleteProject(projectID):
        """
        Delete specific project.

        :param projectID: unique order ID to be deleted
        :type projectID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            #currentUser = User.objects.get(hashedID=userID)
            currentProject = Project.objects.get(projectID=projectID)
            currentProject.delete()
            return True
        except (ObjectDoesNotExist) as error:
            return None
        except (Exception) as error:
            print(error)
        return False

    ##############################################
    @staticmethod
    def updateProject(projectID, updateType: EnumUpdates, content):
        """
        Change details of an project like its status. 

        :param projectID: project ID that this order belongs to
        :type projectID: str
        :param updateType: changed order details
        :type updateType: EnumUpdates
        :param content: changed order, can be many stuff
        :type content: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            if updateType == EnumUpdates.status:
                currentProject = Project.objects.get(projectID=projectID)
                currentProject.status = content
                currentProject.updatedWhen = updated
                currentProject.save()
                # # update status for orders of that collection as well
                # for order in currentOrderCollection.orders.all():
                #     order.status = content
                #     order.updatedWhen = updated
                #     order.save()
            elif updateType == EnumUpdates.details:
                currentProject = Project.objects.get(projectID=projectID)
                for key in content:
                    currentProject.details[key] = content[key]
                currentProject.updatedWhen = updated
                currentProject.save()
            return True
        except (Exception) as error:
            print(error)
            return error
    
    ##############################################
    @staticmethod
    def updateProcess(processID, updateType: EnumUpdates, content):
        """
        Change details of an order like its status, or save communication. 

        :param orderID: unique order ID to be edited
        :type orderID: str
        :param updateType: changed order details
        :type updateType: EnumUpdates
        :param content: changed order, can be many stuff
        :type content: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            currentProcess = Process.objects.get(processID=processID)
            currentProcess.updatedWhen = updated

            if updateType == EnumUpdates.chat:
                currentProcess.messages["messages"].append(content)
            
            elif updateType == EnumUpdates.status:
                currentProcess.status = content
                
                # # if at least one order is being processed, the collection is set to 'in process'
                # respectiveOrderCollection = currentOrder.orderCollectionKey
                # if respectiveOrderCollection.status == 0 and content != 0:
                #     respectiveOrderCollection.status = 1
                #     respectiveOrderCollection.save()
                
                # # if order is set to finished, check if the whole collection can be set to 'finished'
                # finishedFlag = True
                # for orderOfCollection in respectiveOrderCollection.orders.all():
                #     if orderOfCollection.status != 6:
                #         finishedFlag = False
                #         break
                # if finishedFlag:
                #     respectiveOrderCollection.status = 3
            elif updateType == EnumUpdates.files:
                currentProcess.files = content
                
            elif updateType == EnumUpdates.service:
                for entry in content:
                    currentProcess.service[entry] = content[entry]

            elif updateType == EnumUpdates.contractor:
                currentProcess.contractor = content

            elif updateType == EnumUpdates.details:
                for entry in content:
                    currentProcess.details[entry] = content[entry]

            currentProcess.save()
            return True
        except (Exception) as error:
            print(error)
            return error
    
    ##############################################
    @staticmethod
    def deleteFromProcess(processID, updateType: EnumUpdates, content):
        """
        Delete details of an order like its status, or content. 

        :param processID: unique order ID to be edited
        :type processID: str
        :param updateType: changed order details
        :type updateType: EnumUpdates
        :param content: deletions
        :type content: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            currentProcess = Process.objects.get(processID=processID)
            currentProcess.updatedWhen = updated

            if updateType == EnumUpdates.chat:
                currentProcess.messages["messages"].remove(content)
            
            elif updateType == EnumUpdates.status:
                currentProcess.status = 0
                
                # # if at least one order is being processed, the collection is set to 'in process'
                # respectiveOrderCollection = currentOrder.orderCollectionKey
                # if respectiveOrderCollection.status == 0 and content != 0:
                #     respectiveOrderCollection.status = 1
                #     respectiveOrderCollection.save()
                
                # # if order is set to finished, check if the whole collection can be set to 'finished'
                # finishedFlag = True
                # for orderOfCollection in respectiveOrderCollection.orders.all():
                #     if orderOfCollection.status != 6:
                #         finishedFlag = False
                #         break
                # if finishedFlag:
                #     respectiveOrderCollection.status = 3
            elif updateType == EnumUpdates.files:
                currentProcess.files = []
                
            elif updateType == EnumUpdates.service:
                if len(content) > 0:
                    for entry in content:
                        del currentProcess.service[entry]
                else:
                    currentProcess.service = {}

            elif updateType == EnumUpdates.contractor:
                currentProcess.contractor = []

            elif updateType == EnumUpdates.details:
                for key in content:
                    del currentProcess.details[key]

            currentProcess.save()
            return True
        except (Exception) as error:
            print(error)
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
            
            # if it does, create order
            selectedManufacturer = template["contractor"]
            processID = template["processID"]
            service = template["service"]
            status = template["state"]
            serviceStatus = template["serviceStatus"]
            messages = template["messages"]
            files = template["files"]
            details = template["details"]
            processObj = Process.objects.create(processID=processID, projectKey=projectObj, service=service, status=status, serviceStatus=serviceStatus, messages=messages, details=details, files=files, client=clientID, contractor=selectedManufacturer, updatedWhen=timezone.now())
            return None
        except (Exception) as error:
            print(error)
            return error


    ##############################################
    @staticmethod
    def getInfoAboutProjectForWebsocket(projectID):
        """
        Retrieve information about the users connected to the order from the database. 

        :param projectID: project ID to retrieve data from
        :type projectID: str
        :return: Dictionary of users with project ID and processes in order for the websocket to fire events
        :rtype: Dict

        """
        # outputList for events
        dictForEventsAsOutput = {}

        projectObj = Project.objects.get(projectID=projectID)
        dictForEventsAsOutput[projectObj.client] = {"eventType": "orderEvent"}
        dictForEventsAsOutput[projectObj.client]["processes"] = []
        dictForEventsAsOutput[projectObj.client]["projectID"] = projectID
        for process in projectObj.orders.all():
            if projectObj.client != process.client:
                if process.client not in dictForEventsAsOutput:
                    dictForEventsAsOutput[process.client] = {"eventType": "orderEvent"}
                    dictForEventsAsOutput[process.client]["process"] = [{"processID": process.orderID, "status": 1, "messages": 0}]
                    dictForEventsAsOutput[process.client]["projectID"] = projectID
                else:
                    dictForEventsAsOutput[process.client]["processes"].append({"processID": process.orderID, "status": 1, "messages": 0})
            else:
                dictForEventsAsOutput[projectObj.client]["processes"].append({"processID": process.orderID, "status": 1, "messages": 0})
            
            for contractor in process.contractor:
                if projectObj.client != contractor:
                    if contractor not in dictForEventsAsOutput:
                        dictForEventsAsOutput[contractor] = {"eventType": "orderEvent"}
                        dictForEventsAsOutput[contractor]["processes"] = [{"processID": process.orderID, "status": 1, "messages": 0}]
                        dictForEventsAsOutput[contractor]["projectID"] = projectID
                    else:
                        dictForEventsAsOutput[contractor]["processes"].append({"processID": process.orderID, "status": 1, "messages": 0})

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

                projectObj, flag = Project.objects.get_or_create(projectID=projectID, defaults={"status": existingObj["state"], "updatedWhen": now, "client": client.hashedID, "details": existingObj["details"]})
                # retrieve files
                # uploadedFiles = []
                # (contentOrError, Flag) = redis.retrieveContent(session.session_key)
                # if Flag:
                #     for entry in contentOrError:
                #         uploadedFiles.append({"filename":entry[1], "path": session.session_key})

                # save subOrders
                for entry in session["currentProjects"][projectID]["processes"]:
                    process = session["currentProjects"][projectID]["processes"][entry]
                    selectedManufacturer = process["contractor"]
                    processID = process["processID"]
                    service = process["service"]
                    status = process["state"]
                    serviceStatus = process["serviceStatus"]
                    messages = process["messages"]
                    files = process["files"]
                    details = process["details"]
                    processObj, flag = Process.objects.get_or_create(processID=processID, defaults={"projectKey":projectObj, "service": service, "status": status, "messages": messages, "serviceStatus": serviceStatus, "details": details, "files": files, "client": client.hashedID, "contractor": selectedManufacturer, "updatedWhen": now})
                    for contractor in selectedManufacturer:
                        contractorObj = Organization.objects.get(hashedID=contractor)
                        contractorObj.processesReceived.add(processObj)
                        contractorObj.save()
                    
                # link project to client
                client.projects.add(projectObj)
                client.save()

            return None
        except (Exception) as error:
            print(error)
            return error

    ##############################################
    @staticmethod
    def getProcesses(session):
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
                currentProject["state"] = project.status
                currentProject["details"] = project.details
                processesOfThatProject = []
                for entry in project.processes.all():
                    currentProcess = {}
                    currentProcess["client"] = entry.client
                    currentProcess["processID"] = entry.processID
                    currentProcess["contractor"] = entry.contractor
                    currentProcess["service"] = entry.service
                    currentProcess["state"] = entry.status
                    currentProcess["serviceState"] = entry.serviceState
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
            print(error)
        
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
                currentProject["orderID"] = project.projectID
                currentProject["created"] = str(project.createdWhen)
                currentProject["updated"] = str(project.updatedWhen)
                currentProject["state"] = project.status
                currentProject["client"] = project.client
                currentProject["details"] = project.details
                currentProject["processesCount"] = len(project.processes.all())
                    
                output.append(currentProject)
            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["created"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output

        except (Exception) as error:
            print(error)
        
        return []

####################################################################################
# Orders from and for Organizations
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

            # then go through order Collections
            for projectID in session["currentProjects"]:

                # order collection object
                existingObj = session["currentProjects"][projectID]
                projectObj, flag = Project.objects.get_or_create(projectID=projectID, defaults={"status": existingObj["state"], "updatedWhen": now, "client": client.hashedID, "details": existingObj["details"]})
                # retrieve files
                # uploadedFiles = []
                # (contentOrError, Flag) = redis.retrieveContent(session.session_key)
                # if Flag:
                #     for entry in contentOrError:
                #         uploadedFiles.append({"filename":entry[1], "path": session.session_key})

                # save subOrders
                for entry in session["currentProjects"][projectID]["processes"]:
                    process = session["currentProjects"][projectID]["processes"][entry]
                    selectedManufacturer = process["contractor"]
                    processID = process["processID"]
                    service = process["service"]
                    status = process["state"]
                    serviceStatus = process["serviceStatus"]
                    messages = process["chat"]
                    files = process["files"]
                    dates = {"created": process["created"], "updated": str(now)}
                    details = process["details"]
                    processObj, flag = Process.objects.get_or_create(processID=processID, defaults={"projectKey": projectObj, "service": service, "status": status, "serviceStatus": serviceStatus, "messages": messages, "dates": dates, "details": details, "files": files, "client": client.hashedID, "contractor": selectedManufacturer, "updatedWhen": now})

                    for contractor in selectedManufacturer:
                        contractorObj = Organization.objects.get(hashedID=contractor)
                        contractorObj.processesReceived.add(processObj)
                        contractorObj.save()
            
                # link OrderCollection to client
                client.projectsSubmitted.add(projectObj)
                client.save()

            return None
        except (Exception) as error:
            print(error)
            return error
    

    ##############################################
    @staticmethod
    def getProcesses(session):
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
                currentProject["state"] = project.status
                currentProject["client"] = project.client
                currentProject["details"] = project.details
                processesOfThatProject = []
                for entry in project.processes.all():
                    currentProcess = {}
                    currentProcess["processID"] = entry.processID
                    currentProcess["contractor"] = entry.contractor
                    currentProcess["client"] = entry.client
                    currentProcess["service"] = entry.service
                    currentProcess["state"] = entry.status
                    currentProcess["serviceState"] = entry.serviceState
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
                project = processEntry.projectKey

                if project.projectID not in receivedProjects:
                    receivedProjects[project.projectID] = {"projectID": project.projectID, "client": project.client, "created": str(project.createdWhen), "updated": str(project.updatedWhen), "state": project.status, "processes": []}

                currentProcess = {}
                currentProcess["processID"] = processEntry.processID
                currentProcess["contractor"] = processEntry.contractor
                currentProcess["client"] = processEntry.client
                currentProcess["service"] = processEntry.service
                currentProcess["state"] = processEntry.status
                currentProcess["serviceState"] = processEntry.serviceState
                currentProcess["created"] = str(processEntry.createdWhen)
                currentProcess["updated"] = str(processEntry.updatedWhen)
                currentProcess["messages"] = processEntry.messages
                currentProcess["details"] = processEntry.details
                currentProcess["files"] = processEntry.files

                receivedProjects[project.projectID]["processes"].append(currentProcess)
            
            # after collection the projects and their processes, we need to add them to the output
            for project in receivedProjects:
                output.append(project)


            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["created"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output

        except (Exception) as error:
            print(error)
        
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
                currentProject["state"] = project.status
                currentProject["client"] = project.client
                currentProject["details"] = project.details
                currentProject["processesCount"] = len(list(project.processes.all()))

                output.append(currentProject)

            # get received processes
            receivedProcesses = currentUser.processesReceived.all()
            # since multiple processes could have been received within the same project, we need to collect those
            receivedProjects = {}
            for processEntry in receivedProcesses:
                project = processEntry.projectKey

                if project.projectID not in receivedProjects:
                    receivedProjects[project.projectID] = {"projectID": project.projectID, "client": project.client, "created": str(project.createdWhen), "updated": str(project.updatedWhen), "details": project.details, "state": project.status, "processesCount": 0}
                receivedProjects[project.projectID]["processesCount"] += 1
            
            # after collection the projects and their processes, we need to add them to the output
            for project in receivedProjects:
                currentProject = {}
                currentProject["projectID"] = receivedProjects[project]["projectID"]
                currentProject["created"] = receivedProjects[project]["created"]
                currentProject["updated"] = receivedProjects[project]["updated"]
                currentProject["state"] = receivedProjects[project]["state"]
                currentProject["client"] = receivedProjects[project]["client"]
                currentProject["details"] = receivedProjects[project]["details"]
                currentProject["processesCount"] = receivedProjects[project]["processesCount"]

                output.append(currentProject)


            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["created"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output

        except (Exception) as error:
            print(error)
        
        return []
    
processManagement= {"user": ProcessManagementUser(), "organization": ProcessManagementOrganization()}
