"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls
"""
import types

from django.utils import timezone

from ..modelFiles.profile import User,Manufacturer,Stakeholder
from ..modelFiles.orders import Orders,OrderCollection

from backend_django.services import crypto

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
    def getUserID(session):
        """
        Retrieve hashed User ID from Session

        :param session: session
        :type session: Dictionary
        :return: Hashed user key from database
        :rtype: Dictionary

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
        # TODO
        if "organizationType" in session:
            organizationType = session["organizationType"]
            organization = session["usertype"]
        else:
            organizationType = "None"
            organization = "None"

        role = "standard"
        address = {"country": "Germany", "city": "Leipzig", "zipcode": "12345", "street": "Nowherestreet", "number": "42"}
        updated = timezone.now()
        try:
            # first get, then create
            result = User.objects.get(subID=userID)
        except (Exception) as error:
            try:
                idHash = crypto.generateSecureID(userID)
                createdUser = User.objects.create(subID=userID, hashedID=idHash, name=userName, email=userEmail, role=role, organization=organization, address=address, updatedWhen=updated) 
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
# Orders
class OrderManagement():
    ##############################################
    @staticmethod
    def addOrder(userID, manufacturerID, orderFromUser):
        """
        Add order for that user. Check if user already has orders and append if so, create a new user if not.

        :param userID: user ID of a user
        :type userID: str
        :param orderID: unique order collection ID
        :type orderID: str
        :param orderFromUser: order details
        :type orderFromUser: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """

        now = timezone.now()
        try:
            # first get user and manufacturer
            userThatOrdered = User.objects.get(subID=userID)
            selectedManufacturer = Manufacturer.objects.get(subID=manufacturerID)
            # generate key and order collection
            orderCollectionID = crypto.generateMD5(str(orderFromUser) + crypto.generateSalt())
            collectionObj = OrderCollection.objects.create(orderCollectionID=orderCollectionID, status="requested", updatedWhen=now)
            # generate orders
            for entry in orderFromUser:
                orderID = crypto.generateMD5(str(entry) + crypto.generateSalt())
                userOrders = entry
                status = "requested"
                userCommunication = {}
                files = []
                dates = {"created": str(now), "updated": str(now)}
                Orders.objects.create(orderID=orderID, orderCollectionKey=collectionObj, userOrders=userOrders, status=status, userCommunication=userCommunication, files=files, dates=dates, updatedWhen=now)
            # link OrderCollection to user and all users of a manufacturer
            userThatOrdered.orders.add(collectionObj)
            # selectedManufacturer.users_set.all() orders.add(collectionObj) #TODO
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
        :return: Tuple with all jsons (orders, status, communication, files)
        :rtype: Tuple of JSONs

        """
        try:
            # get user
            currentUser = User.objects.get(uID=userID)
            # get associated OrderCollections
            orderCollections = currentUser.orders.all()
            for order in orderCollections:
                print(order)
            #return [result.userOrders, result.orderStatus, result.userCommunication, result.files, result.dates]
        except (Exception) as error:
            print(error)
        
        return [{}, {}, {}, {}, {}]

    ##############################################
    @staticmethod
    def deleteOrder(userID, orderID):
        """
        Delete specific order for a user.

        :param userID: user ID as primary key for search
        :type userID: str
        :param orderID: unique order ID to be deleted
        :type orderID: str
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            # result = Orders.objects.get(uID=userID)
            # result.orderIDs.remove(orderID)
            # result.userOrders.pop(orderID)
            # result.orderStatus.pop(orderID)
            # result.userCommunication.pop(orderID)
            # result.files.pop(orderID)
            # result.dates.pop(orderID)
            # Orders.objects.filter(uID=userID).update(orderIDs=result.orderIDs, userOrders=result.userOrders, orderStatus=result.orderStatus, userCommunication=result.userCommunication, files=result.files, updatedWhen=updated)
            return True
        except (Exception) as error:
            print(error)
        return False

    ##############################################
    @staticmethod
    def updateOrder(userID, orderID, orderFromUser={}, orderStatus={}, userCommunications={}, files={}):
        """
        Change details of an order, its status, or save communication 

        :param userID: user ID as primary key for search
        :type userID: str
        :param orderID: unique order ID to be edited
        :type orderID: str
        :param orderFromUser: changed order details
        :type orderFromUser: json dict
        :param orderStatus: changed order status
        :type orderStatus: json dict
        :param userCommunications: new communication for that order
        :type userCommunications: json dict
        :param files: new file has been uploaded for an order
        :type files: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """
        updated = timezone.now()
        try:
            # result = Orders.objects.get(uID=userID)
            # # edit one after another
            # result.dates[orderID]["updated"] = str(updated)
            # if orderFromUser != {}:
            #     result.userOrders[orderID] = orderFromUser
            #     Orders.objects.filter(uID=userID).update(userOrders=result.userOrders, dates=result.dates, updatedWhen=updated)
            # if orderStatus != {}:
            #     result.orderStatus[orderID] = orderStatus
            #     Orders.objects.filter(uID=userID).update(orderStatus=result.orderStatus, dates=result.dates, updatedWhen=updated)
            # if userCommunications != {}:
            #     result.userCommunication[orderID] = userCommunications
            #     Orders.objects.filter(uID=userID).update(userCommunication=result.userCommunication, dates=result.dates, updatedWhen=updated)
            # if files != {}:
            #     result.files[orderID] = files
            #     Orders.objects.filter(uID=userID).update(files=result.files, dates=result.dates, updatedWhen=updated)
            return True
        except (Exception) as error:
            print(error)
        return False