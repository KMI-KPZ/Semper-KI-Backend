"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls
"""
import types, json, enum, re

from datetime import datetime
from django.utils import timezone

from ..modelFiles.profile import User,Manufacturer,Stakeholder
from ..modelFiles.orders import Orders,OrderCollection

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
            obj = Manufacturer.objects.all().values("hashedID", "name", "address")
        except (Exception) as error:
            print(error)

        return obj
    
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
        Sets the accessed Time to now. Used for 'Last Login'.

        :param session: userID
        :type session: str
        :return: Nothing
        :rtype: None

        """
        currUser = User.objects.get(hashedID=userIDHash)
        currUser.save()

    ##############################################
    @staticmethod
    def addUser(session):
        """
        Add user if the entry doesn't already exists.

        :param session: POST request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        userID = session["user"]["userinfo"]["sub"]
        userName = session["user"]["userinfo"]["nickname"]
        userEmail = session["user"]["userinfo"]["email"]

        if "organizationType" in session:
            organizationType = session["organizationType"]
            organization = auth0.retrieveOrganisationName(session["user"]["userinfo"]["org_id"])
        else:
            organizationType = "None"
            organization = "None"

        role = session["usertype"]
        rights = {role: "all"}
        address = {"country": "Germany", "city": "Leipzig", "zipcode": "12345", "street": "Nowherestreet", "number": "42"}
        updated = timezone.now()
        try:
            # first get, then create
            result = User.objects.get(subID=userID)
        except (Exception) as error:
            try:
                idHash = crypto.generateSecureID(userID)
                createdUser = User.objects.create(subID=userID, hashedID=idHash, name=userName, email=userEmail, role=role, rights=rights, organization=organization, address=address, updatedWhen=updated) 
                if organizationType != "None":
                    if ProfileManagement.addUserToOrganization(createdUser, organization) == False:
                        if ProfileManagement.addOrganization(session, organizationType):
                            ProfileManagement.addUserToOrganization(createdUser, organization)
                        else:
                            print("User could not be added to organization!", createdUser, organization)
            except (Exception) as error:
                print(error)
                return False
            pass
        return True
    
    ##############################################
    @staticmethod
    def addUserToOrganization(userToBeAdded, organization):
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
            result = Manufacturer.objects.get(subID=organization)
            result.users.add(userToBeAdded)
        except (Exception) as error:
            pass
        try:
            result = Stakeholder.objects.get(subID=organization)
            result.users.add(userToBeAdded)
        except (Exception) as error:
            print("Organization doesn't exist!")
            return False

        return True

    ##############################################
    @staticmethod
    def addOrganization(session, typeOfOrganization):
        """
        Add organization if the entry doesn't already exists.

        :param session: POST request session
        :type session: Dictionary
        :param typeOfOrganization: type of the organization, can be: manufacturer, stakeholder
        :type typeOfOrganization: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        orgaID = session["usertype"]
        orgaName = session["usertype"]
        orgaEmail = "testOrga1@test.org"
        orgaAddress = {"country": "Germany", "city": "Leipzig", "zipcode": "12345", "street": "Nowherestreet", "number": "42"}
        updated = timezone.now()
        try:
            # first get, then create
            if typeOfOrganization == "manufacturer":
                Manufacturer.objects.get(subID=orgaID)
            elif typeOfOrganization == "stakeholder":
                Stakeholder.objects.get(subID=orgaID)
            
        except (Exception) as error:
            try:
                idHash = crypto.generateSecureID(orgaID)
                if typeOfOrganization == "manufacturer":
                    uri = "www.test.org"
                    Manufacturer.objects.create(subID=orgaID, hashedID=idHash, name=orgaName, email=orgaEmail, address=orgaAddress, uri=uri, updatedWhen=updated) 
                elif typeOfOrganization == "stakeholder":
                    Stakeholder.objects.create(subID=orgaID, hashedID=idHash, name=orgaName, email=orgaEmail, address=orgaAddress, updatedWhen=updated) 
            except (Exception) as error:
                print(error)
                return False
            pass
        return True

    ##############################################
    @staticmethod
    def updateName(session, userName):
        """
        Update user name.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        userID = session["user"]["userinfo"]["sub"]
        updated = timezone.now()
        try:
            affected = User.objects.filter(subID=userID).update(name=userName, updatedWhen=updated)
        except (Exception) as error:
            print(error)
            return False
        return True

    ##############################################
    @staticmethod
    def deleteUser(session):
        """
        Delete User.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
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
    def addOrder(userID, orderFromUser, session):
        """
        Add order for that user. Check if user already has orders and append if so, create a new user if not.

        :param userID: user ID of a user
        :type userID: str
        :param orderFromUser: order details
        :type orderFromUser: json dict
        :param session: session of user
        :type session: session dict
        :return: Flag if it worked or not
        :rtype: Bool

        """

        now = timezone.now()
        try:
            # first get user and manufacturer
            userThatOrdered = User.objects.get(hashedID=userID)
            # generate key and order collection
            orderCollectionID = crypto.generateMD5(str(orderFromUser) + crypto.generateSalt())
            collectionObj = OrderCollection.objects.create(orderCollectionID=orderCollectionID, status=0, updatedWhen=now)
            # retrieve files
            uploadedFiles = []
            (contentOrError, Flag) = redis.retrieveContent(session.session_key)
            if Flag:
                for entry in contentOrError:
                    uploadedFiles.append({"filename":entry[1], "path": session.session_key})

            # generate orders
            listOfSelectedManufacturers = []
            for idx, entry in enumerate(orderFromUser):
                selectedManufacturer = Manufacturer.objects.get(hashedID=entry["manufacturerID"])
                listOfSelectedManufacturers.append(selectedManufacturer)
                orderID = crypto.generateMD5(str(entry) + crypto.generateSalt())
                userOrders = entry
                status = 0
                userCommunication = {"messages": []}
                if len(uploadedFiles) != 0:
                    files = [uploadedFiles[idx]]
                else:
                    files = []
                dates = {"created": str(now), "updated": str(now)}
                Orders.objects.create(orderID=orderID, orderCollectionKey=collectionObj, userOrders=userOrders, status=status, userCommunication=userCommunication, files=files, dates=dates, updatedWhen=now)
            # link OrderCollection to user
            userThatOrdered.orders.add(collectionObj)
            userThatOrdered.save()
            # link OrderCollection to every eligible user of every selected manufacturer
            for manufacturer in listOfSelectedManufacturers:
                testresult = manufacturer.users.all() 
                for entry in testresult:
                    # todo get rights to check if okay that this user can see this
                    entry.orders.add(collectionObj)
                    entry.save()
        except (Exception) as error:
            print(error)
            return False
        return True

    ##############################################
    @staticmethod
    def getOrders(userID):
        """
        Get all orders for that user.

        :param userID: user ID for a user
        :type userID: str
        :return: sorted list with all jsons (orders, status, communication, files)
        :rtype: list

        """
        try:
            # get user
            currentUser = User.objects.get(hashedID=userID)
            # get associated OrderCollections
            output = []
            orderCollections = currentUser.orders.all()
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
        Get all users that are connected to that orderID.

        :param orderID: unique order ID
        :type orderID: str
        :return: List of all userIDs
        :rtype: List

        """
        try:
            currentOrder = Orders.objects.get(orderID=orderID)
            users = User.objects.filter(orders=currentOrder.orderCollectionKey).all()
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
                    
                    # if order is set to finished, check if the whole collection ca be set to 'finished'
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