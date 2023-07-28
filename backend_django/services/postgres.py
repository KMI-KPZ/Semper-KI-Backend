"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls
"""
import types, json, enum, re

from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from ..modelFiles.profileModel import User, Organization
from ..modelFiles.ordersModel import Orders, OrderCollection

from backend_django.services import crypto, redis, auth0

#TODO: switch to async versions at some point

####################################################################################
# Profile
class ProfileManagement():

    ##############################################
    @staticmethod
    def getUser(session):
        """
        Check whether a user exists or not.

        :param session: session
        :type session: Dictionary
        :return: User details from database
        :rtype: Dictionary

        """
        userID = session["user"]["userinfo"]["sub"]
        obj = {}
        try:
            obj = User.objects.get(subID=userID).toDict()
        except (Exception) as error:
            print(error)

        return obj
    
    ##############################################
    @staticmethod
    def getAllManufacturers(session):
        """
        Get all manufacturers.
        :param session: Session
        :type session: Dictionary
        :return: All manufacturers
        :rtype: Dictionary

        """
        obj = {}
        try:
            listOfManufacturers = Organization.objects.filter(canManufacture=True)
            returnValue = []
            for entry in listOfManufacturers:
                returnValue.append({"hashedID": entry.hashedID, "name": entry.name, "details": entry.details})
        except (Exception) as error:
            print(error)

        return returnValue
    
    ##############################################
    @staticmethod
    def getUserHashID(session):
        """
        Retrieve hashed User ID from Session

        :param session: session
        :type session: Dictionary
        :return: Hashed user key from database
        :rtype: Str

        """
        hashID = ""
        try:
            userID = session["user"]["userinfo"]["sub"]
            hashID = User.objects.get(subID=userID).hashedID
        except (Exception) as error:
            print(error)

        return hashID
    
    ##############################################
    @staticmethod
    def getUserKey(session):
        """
        Retrieve User ID from Session

        :param session: session
        :type session: Dictionary
        :return: User key from database
        :rtype: Str

        """
        userID = ""
        try:
            userID = session["user"]["userinfo"]["sub"]
        except (Exception) as error:
            print(error)

        return userID
    
    ##############################################
    @staticmethod
    def getUserKeyWOSC(session=None, uID=None):
        """
        Retrieve User ID from Session without special characters

        :param session: session
        :type session: Dictionary
        :return: User key from database without stuff like | or ^
        :rtype: Str

        """
        userID = ""
        try:
            if session is not None:
                userID = session["user"]["userinfo"]["sub"]
            if uID is not None:
                userID = uID
            userID = re.sub(r"[^a-zA-Z0-9]", "", userID)
        except (Exception) as error:
            print(error)

        return userID
    
    ##############################################
    @staticmethod
    def setLoginTime(userIDHash):
        """
        Sets the las login Time to now. Used for 'Last Login'.

        :param session: userID
        :type session: str
        :return: Nothing
        :rtype: None

        """
        currUser = User.objects.get(hashedID=userIDHash)
        currUser.lastSeen = timezone.now()
        currUser.save()

    ##############################################
    @staticmethod
    def addUserIfNotExists(session, organization=None):
        """
        Add user if the entry doesn't already exists.

        :param session: POST request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """

        userID = session["user"]["userinfo"]["sub"]
        try:
            # first get, then create
            result = User.objects.get(subID=userID)
        except (ObjectDoesNotExist) as error:
            try:
                userName = session["user"]["userinfo"]["nickname"]
                userEmail = session["user"]["userinfo"]["email"]
                details = {}
                updated = timezone.now()
                lastSeen = timezone.now()
                idHash = crypto.generateSecureID(userID)
                 
                if organization != None:
                    createdUser = User.objects.create(subID=userID, hashedID=idHash, name=userName, email=userEmail, organizations=[organization.subID], details=details, updatedWhen=updated, lastSeen=lastSeen)
                    if ProfileManagement.addUserToOrganization(createdUser, session["user"]["userinfo"]["org_id"]) == False:
                        raise Exception(f"User could not be added to organization!, {createdUser}, {organization}")
                else:
                    createdUser = User.objects.create(subID=userID, hashedID=idHash, name=userName, email=userEmail, organizations=["None"], details=details, updatedWhen=updated, lastSeen=lastSeen)

            except (Exception) as error:
                print(error)
                return False
            pass
        return True
    
    ##############################################
    @staticmethod
    def addUserToOrganization(userToBeAdded, organizationID):
        """
        Add user to organization.

        :param userToBeAdded: User to be added
        :type userToBeAdded: User
        :param organization: id of the organization
        :type organization: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        try:
            result = Organization.objects.get(subID=organizationID)
            result.users.add(userToBeAdded)
        except (ObjectDoesNotExist) as error:
            print("Organization doesn't exist!", error)
            return False

        return True

    ##############################################
    @staticmethod
    def addOrGetOrganization(session):
        """
        Add organization if the entry doesn't already exists.

        :param session: POST request session
        :type session: Dictionary
        :param typeOfOrganization: type of the organization, can be: manufacturer, stakeholder
        :type typeOfOrganization: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        orgaID = session["user"]["userinfo"]["org_id"]
        updated = timezone.now()
        try:
            # first get, then create
            resultObj = Organization.objects.get(subID=orgaID)
            return resultObj
        except (ObjectDoesNotExist) as error:
            try:
                orgaName = session["organizationName"]
                orgaDetails = {"e-mail": "", "adress": "", "taxID": ""}
                idHash = crypto.generateSecureID(orgaID)
                uri = ""
                resultObj = Organization.objects.create(subID=orgaID, hashedID=idHash, name=orgaName, details=orgaDetails, uri=uri, updatedWhen=updated) 
                return resultObj
            except (Exception) as error:
                print(error)
                return None
        except (Exception) as error:
            print(error)
            return None

    ##############################################
    @staticmethod
    def updateDetails(session, details):
        """
        Update user details.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        userID = session["user"]["userinfo"]["sub"]
        updated = timezone.now()
        try:
            affected = User.objects.filter(subID=userID).update(details=details, updatedWhen=updated)
        except (Exception) as error:
            print(error)
            return False
        return True
    
    ##############################################
    @staticmethod
    def updateDetailsOfOrganisation(session, details):
        """
        Update user details.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        orgID = session["user"]["userinfo"]["org_id"]
        updated = timezone.now()
        try:
            affected = Organization.objects.filter(subID=orgID).update(details=details, updatedWhen=updated)
        except (Exception) as error:
            print(error)
            return False
        return True

    ##############################################
    @staticmethod
    def deleteUser(session, uID=""):
        """
        Delete User.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        if uID != "":
            userID = uID
        else:
            userID = session["user"]["userinfo"]["sub"]
            
        try:
            affected = User.objects.filter(subID=userID).delete()
        except (Exception) as error:
            print(error)
            return False
        return True

####################################################################################
# Enum for updateOrder
class EnumUpdates(enum.Enum):
    status = 1
    chat = 2
    files = 3

# Orders
class OrderManagement():
    ##############################################
    @staticmethod
    def addOrder(orderFromUser, session):
        """
        Add order for that user. Check if user already has orders and append if so, create a new order if not.

        :param userID: user ID of a user
        :type userID: str
        :param orderFromUser: order details
        :type orderFromUser: json dict
        :param session: session of user
        :type session: session dict
        :return: Dictionary of users with order collection id and orders in order for the websocket to fire events
        :rtype: Dict

        """
        now = timezone.now()
        try:
            # outputList for events
            dictForEventsAsOutput = {}

            # first get user or organisation
            if "isPartOfOrganization" in session:
                client = Organization.objects.get(hashedID=session["user"]["userinfo"]["org_id"])
            else:
                client = User.objects.get(hashedID=session["user"]["userinfo"]["sub"])
            
            # generate key and order collection
            orderCollectionID = crypto.generateMD5(str(orderFromUser) + crypto.generateSalt())
            collectionObj = OrderCollection.objects.create(orderCollectionID=orderCollectionID, status=0, updatedWhen=now)
            # retrieve files
            uploadedFiles = []
            (contentOrError, Flag) = redis.retrieveContent(session.session_key)
            if Flag:
                for entry in contentOrError:
                    uploadedFiles.append({"filename":entry[1], "path": session.session_key})

            for idx, entry in enumerate(orderFromUser):
                # generate orders
                selectedManufacturer = Organization.objects.get(hashedID=entry["manufacturerID"])
                orderID = crypto.generateMD5(str(entry) + crypto.generateSalt())
                userOrders = entry
                status = 0
                userCommunication = {"messages": []}
                if len(uploadedFiles) != 0:
                    files = [uploadedFiles[idx]]
                else:
                    files = []
                dates = {"created": str(now), "updated": str(now)}
                ordersObj = Orders.objects.create(orderID=orderID, orderCollectionKey=collectionObj, userOrders=userOrders, status=status, userCommunication=userCommunication, files=files, dates=dates, client=client.hashedID, contractor=[selectedManufacturer.hashedID], updatedWhen=now)
                selectedManufacturer.ordersReceived.add(ordersObj)
                
                # save ID of manufacturers for the websocket events
                if selectedManufacturer.hashedID in dictForEventsAsOutput:
                    dictForEventsAsOutput[selectedManufacturer.hashedID]["orders"].append({"orderID": orderID, "status": 1, "messages": 0})
                else:
                    dictForEventsAsOutput[selectedManufacturer.hashedID] = {"eventType": "orderEvent"}
                    dictForEventsAsOutput[selectedManufacturer.hashedID]["orders"] = [{"orderID": orderID, "status": 1, "messages": 0}]
                    dictForEventsAsOutput[selectedManufacturer.hashedID]["orderCollectionID"] = orderCollectionID

            # link OrderCollection to client
            if "isPartOfOrganization" in session:
                client.ordersSubmitted.add(collectionObj)
            else:
                client.orders.add(collectionObj)
            client.save()

            return dictForEventsAsOutput
        except (Exception) as error:
            print(error)
            return {}

    ##############################################
    @staticmethod
    def getOrders(session):
        """
        TODO
        Get all orders for that user.

        :param session: session of that user
        :type session: dict
        :return: sorted list with all jsons (orders, status, communication, files)
        :rtype: list

        """
        try:
            # get user
            if "isPartOfOrganization" in session:
                currentUser = Organization.objects.get(hashedID=session["user"]["userinfo"]["org_id"])
                orderCollections = currentUser.orders.all()
            else:
                currentUser = User.objects.get(hashedID=session["user"]["userinfo"]["sub"])
                orderCollections = currentUser.orders.all()
            # get associated OrderCollections
            output = []
            
            for orderCollection in orderCollections:
                currentOrderCollection = {}
                currentOrderCollection["id"] = orderCollection.orderCollectionID
                currentOrderCollection["date"] = str(orderCollection.createdWhen)
                currentOrderCollection["state"] = orderCollection.status
                ordersOfThatCollection = []
                for entry in orderCollection.orders.all():
                    currentOrder = {}
                    currentOrder["id"] = entry.orderID
                    currentOrder["item"] = entry.userOrders
                    currentOrder["orderState"] = entry.status
                    currentOrder["chat"] = entry.userCommunication
                    filesOutput = []
                    if len(entry.files) != 0:
                        for elem in entry.files:
                            filesOutput.append(elem["filename"])
                    currentOrder["files"] = filesOutput
                    currentOrder["updatedWhen"] = entry.updatedWhen
                    currentOrder["createdWhen"] = entry.createdWhen
                    #currentOrder["dates"] = json.dumps(entry.dates)
                    ordersOfThatCollection.append(currentOrder)
                currentOrderCollection["orders"] = ordersOfThatCollection
                output.append(currentOrderCollection)
            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["date"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output
            #return [result.userOrders, result.orderStatus, result.userCommunication, result.files, result.dates]
        except (Exception) as error:
            print(error)
        
        return []
    
    ##############################################
    @staticmethod
    def getOrder(orderID):
        """
        Get one order.

        :param orderID: order ID for an order
        :type orderID: str
        :return: Requested order
        :rtype: Order

        """
        try:
            currentOrder = Orders.objects.get(orderID=orderID)
            return currentOrder
        except (Exception) as error:
            print(error)
        
        return None

    ##############################################
    @staticmethod
    def getAllUsersOfOrder(orderID):
        """
        TODO
        Get all users that are connected to that orderID.

        :param orderID: unique order ID
        :type orderID: str
        :return: List of all userIDs
        :rtype: List

        """
        try:
            currentOrder = Orders.objects.get(orderID=orderID)

            users = list(User.objects.filter(orders=currentOrder.orderCollectionKey).all())
            users.extend(list(Organization.objects.filter(ordersSubmitted=currentOrder.orderCollectionKey).all()))
            return list(users)
        except (Exception) as error:
            print(error)
        return []

    ##############################################
    @staticmethod
    def deleteOrder(orderID):
        """
        Delete specific order.

        :param orderID: unique order ID to be deleted
        :type orderID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            currentOrder = Orders.objects.get(orderID=orderID)
            if len(currentOrder.orderCollectionKey.orders.all()) == 1:
                currentOrder.orderCollectionKey.delete()
            else:
                currentOrder.orderCollectionKey.updatedWhen = updated
                currentOrder.delete()
            return True
        except (Exception) as error:
            print(error)
        return False
    
    ##############################################
    @staticmethod
    def deleteOrderCollection(orderCollectionID):
        """
        Delete specific orderCollection.

        :param orderCollectionID: unique order ID to be deleted
        :type orderCollectionID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            #currentUser = User.objects.get(hashedID=userID)
            currentOrderCollection = OrderCollection.objects.get(orderCollectionID=orderCollectionID)
            currentOrderCollection.delete()
            return True
        except (Exception) as error:
            print(error)
        return False

    ##############################################
    @staticmethod
    def updateOrder(orderID, orderCollectionID, updateType: EnumUpdates, content):
        """
        TODO
        Change details of an order, its status, or save communication 

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
            if updateType == EnumUpdates.chat:
                currentOrder = Orders.objects.get(orderID=orderID)
                currentOrder.userCommunication["messages"].append(content)
                currentOrder.updatedWhen = updated
                currentOrder.save()
            elif updateType == EnumUpdates.status:
                if orderID != "":
                    currentOrder = Orders.objects.get(orderID=orderID)
                    currentOrder.status = content
                    currentOrder.updatedWhen = updated
                    currentOrder.save()
                    
                    # if at least one order is being processed, the collection is set to 'in process'
                    respectiveOrderCollection = currentOrder.orderCollectionKey
                    if respectiveOrderCollection.status == 0 and content != 0:
                        respectiveOrderCollection.status = 1
                        respectiveOrderCollection.save()
                    
                    # if order is set to finished, check if the whole collection can be set to 'finished'
                    finishedFlag = True
                    for orderOfCollection in respectiveOrderCollection.orders.all():
                        if orderOfCollection.status != 6:
                            finishedFlag = False
                            break
                    if finishedFlag:
                        respectiveOrderCollection.status = 3

                elif orderCollectionID != "":    
                    currentOrderCollection = OrderCollection.objects.get(orderCollectionID=orderCollectionID)
                    currentOrderCollection.status = content
                    currentOrderCollection.updatedWhen = updated
                    currentOrderCollection.save()
                    # update status for orders of that collection as well
                    for order in currentOrderCollection.orders.all():
                        order.status = content
                        order.updatedWhen = updated
                        order.save()
            return True
        except (Exception) as error:
            print(error)
        return False