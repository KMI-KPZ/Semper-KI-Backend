"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls
"""
import enum

from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from ...modelFiles.profileModel import User, Organization
from ...modelFiles.ordersModel import Orders, OrderCollection

from backend_django.services import crypto, redis

#TODO: switch to async versions at some point

####################################################################################
# Enum for updateOrder
class EnumUpdates(enum.Enum):
    status = 1
    chat = 2
    files = 3

####################################################################################
# Orders general
class OrderManagementBase():
    
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
        except (ObjectDoesNotExist) as error:
            return None
        except (Exception) as error:
            print(error)
        
        return None
    
    ##############################################
    @staticmethod
    def getOrderCollection(orderCollectionID):
        """
        Get one orderCollection object.

        :param orderID: order collection ID for an order collection
        :type orderID: str
        :return: Requested orderCollection object
        :rtype: Order

        """
        try:
            currentOrderCollection = OrderCollection.objects.get(orderCollectionID=orderCollectionID)
            return currentOrderCollection
        except (ObjectDoesNotExist) as error:
            return None
        except (Exception) as error:
            print(error)
        
        return None

    ##############################################
    @staticmethod
    def getOrder(orderCollectionID):
        """
        Get info about one order collection.

        :param orderCollectionID: ID of the order collection
        :type orderCollectionID: str
        :return: dict with info about that order collection
        :rtype: dict

        """
        try:
            # get order collection
            orderCollection = OrderCollection.objects.get(orderCollectionID=orderCollectionID)

            output = {}
            
            output["orderID"] = orderCollection.orderCollectionID
            output["created"] = str(orderCollection.createdWhen)
            output["updated"] = str(orderCollection.updatedWhen)
            output["client"] = orderCollection.client
            output["state"] = orderCollection.status
            ordersOfThatCollection = []
            for entry in orderCollection.orders.all():
                currentOrder = {}
                currentOrder["client"] = entry.client
                currentOrder["subOrderID"] = entry.orderID
                currentOrder["contractor"] = entry.contractor
                currentOrder["service"] = entry.userOrders
                currentOrder["state"] = entry.status
                currentOrder["created"] = str(entry.createdWhen)
                currentOrder["updated"] = str(entry.updatedWhen)
                currentOrder["chat"] = entry.userCommunication
                currentOrder["details"] = entry.details
                currentOrder["files"] = entry.files
                ordersOfThatCollection.append(currentOrder)
            output["subOrders"] = ordersOfThatCollection
            
            return output

        except (Exception) as error:
            print(error)
        
        return {}

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

            users = list(User.objects.filter(hashedID=currentOrder.client).all())
            users.extend(list(Organization.objects.filter(hashedID=currentOrder.client).all()))
            users.extend(list(Organization.objects.filter(hashedID=currentOrder.contractor).all()))
            return users
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
        Change details of an order or orderCollection like its status, or save communication.
        If orderID == "" the orderCollectionID is relevant and vice versa. 

        :param orderID: unique order ID to be edited
        :type orderID: str
        :param orderCollectionID: orderCollection ID that this order belongs to
        :type orderCollectionID: str
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
    
####################################################################################
# Orders from User
class OrderManagementUser(OrderManagementBase):
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
        #TODO
        now = timezone.now()
        try:
            # outputList for events
            dictForEventsAsOutput = {}

            # first get user
            client = User.objects.get(subID=session["user"]["userinfo"]["sub"])
            
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
                    files = {"files": [uploadedFiles[idx]]}
                else:
                    files = {"files": []}
                dates = {"created": str(now), "updated": str(now)}
                details = {}
                ordersObj = Orders.objects.create(orderID=orderID, orderCollectionKey=collectionObj, userOrders=userOrders, status=status, userCommunication=userCommunication, details=details, files=files, dates=dates, client=client.hashedID, contractor=[selectedManufacturer.hashedID], updatedWhen=now)
                selectedManufacturer.ordersReceived.add(ordersObj)
                
                # save ID of manufacturers for the websocket events
                if selectedManufacturer.hashedID in dictForEventsAsOutput:
                    dictForEventsAsOutput[selectedManufacturer.hashedID]["orders"].append({"orderID": orderID, "status": 1, "messages": 0})
                else:
                    dictForEventsAsOutput[selectedManufacturer.hashedID] = {"eventType": "orderEvent"}
                    dictForEventsAsOutput[selectedManufacturer.hashedID]["orders"] = [{"orderID": orderID, "status": 1, "messages": 0}]
                    dictForEventsAsOutput[selectedManufacturer.hashedID]["orderCollectionID"] = orderCollectionID

            # link OrderCollection to client
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
        Get all orders for that user.

        :param session: session of that user
        :type session: dict
        :return: sorted list with all orders
        :rtype: list

        """
        try:
            # get user
            currentUser = User.objects.get(subID=session["user"]["userinfo"]["sub"])
            orderCollections = currentUser.orders.all()
            # get associated OrderCollections
            output = []
            
            for orderCollection in orderCollections:
                currentOrderCollection = {}
                currentOrderCollection["orderID"] = orderCollection.orderCollectionID
                currentOrderCollection["created"] = str(orderCollection.createdWhen)
                currentOrderCollection["updated"] = str(orderCollection.updatedWhen)
                currentOrderCollection["client"] = orderCollection.client
                currentOrderCollection["state"] = orderCollection.status
                ordersOfThatCollection = []
                for entry in orderCollection.orders.all():
                    currentOrder = {}
                    currentOrder["client"] = entry.client
                    currentOrder["subOrderID"] = entry.orderID
                    currentOrder["contractor"] = entry.contractor
                    currentOrder["service"] = entry.userOrders
                    currentOrder["state"] = entry.status
                    currentOrder["created"] = str(entry.createdWhen)
                    currentOrder["updated"] = str(entry.updatedWhen)
                    currentOrder["chat"] = entry.userCommunication
                    currentOrder["details"] = entry.details
                    currentOrder["files"] = entry.files
                    ordersOfThatCollection.append(currentOrder)
                currentOrderCollection["subOrders"] = ordersOfThatCollection
                output.append(currentOrderCollection)
            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["date"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output

        except (Exception) as error:
            print(error)
        
        return []
    
    ##############################################
    @staticmethod
    def getOrdersFlat(session):
        """
        Get all orders for that user but with limited detail.

        :param session: session of that user
        :type session: dict
        :return: sorted list with orders
        :rtype: list

        """
        try:
            # get user
            currentUser = User.objects.get(subID=session["user"]["userinfo"]["sub"])
            orderCollections = currentUser.orders.all()
            # get associated OrderCollections
            output = []
            
            for orderCollection in orderCollections:
                currentOrderCollection = {}
                currentOrderCollection["orderID"] = orderCollection.orderCollectionID
                currentOrderCollection["created"] = str(orderCollection.createdWhen)
                currentOrderCollection["updated"] = str(orderCollection.updatedWhen)
                currentOrderCollection["state"] = orderCollection.status
                currentOrderCollection["client"] = orderCollection.client
                currentOrderCollection["subOrderCount"] = len(orderCollection.orders.all())
                    
                output.append(currentOrderCollection)
            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["date"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output

        except (Exception) as error:
            print(error)
        
        return []

####################################################################################
# Orders from and for Organizations
class OrderManagementOrganization(OrderManagementBase):

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
        #TODO
        now = timezone.now()
        try:
            # outputList for events
            dictForEventsAsOutput = {}

            # first get organisation
            client = Organization.objects.get(subID=session["user"]["userinfo"]["org_id"])

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
                    files = {"files": [uploadedFiles[idx]]}
                else:
                    files = {"files": []}
                dates = {"created": str(now), "updated": str(now)}
                details = {}
                ordersObj = Orders.objects.create(orderID=orderID, orderCollectionKey=collectionObj, userOrders=userOrders, status=status, userCommunication=userCommunication, details=details, files=files, dates=dates, client=client.hashedID, contractor=[selectedManufacturer.hashedID], updatedWhen=now)
                selectedManufacturer.ordersReceived.add(ordersObj)
                
                # save ID of manufacturers for the websocket events
                if selectedManufacturer.hashedID in dictForEventsAsOutput:
                    dictForEventsAsOutput[selectedManufacturer.hashedID]["orders"].append({"orderID": orderID, "status": 1, "messages": 0})
                else:
                    dictForEventsAsOutput[selectedManufacturer.hashedID] = {"eventType": "orderEvent"}
                    dictForEventsAsOutput[selectedManufacturer.hashedID]["orders"] = [{"orderID": orderID, "status": 1, "messages": 0}]
                    dictForEventsAsOutput[selectedManufacturer.hashedID]["orderCollectionID"] = orderCollectionID

            # link OrderCollection to client
            client.ordersSubmitted.add(collectionObj)
            client.save()

            return dictForEventsAsOutput
        except (Exception) as error:
            print(error)
            return {}
    
    ##############################################
    @staticmethod
    def getOrders(session):
        """
        Get all orders for that organisation.

        :param session: session of that user
        :type session: dict
        :return: sorted list with all jsons (orders, status, communication, files)
        :rtype: list

        """
        try:
            # get organisation
            currentUser = Organization.objects.get(subID=session["user"]["userinfo"]["org_id"])
            orderCollections = currentUser.ordersSubmitted.all()

            # get associated OrderCollections for submitted orders
            output = []
            
            for orderCollection in orderCollections:
                currentOrderCollection = {}
                currentOrderCollection["orderID"] = orderCollection.orderCollectionID
                currentOrderCollection["created"] = str(orderCollection.createdWhen)
                currentOrderCollection["updated"] = str(orderCollection.updatedWhen)
                currentOrderCollection["state"] = orderCollection.status
                currentOrderCollection["client"] = orderCollection.client
                ordersOfThatCollection = []
                for entry in orderCollection.orders.all():
                    currentOrder = {}
                    currentOrder["subOrderID"] = entry.orderID
                    currentOrder["contractor"] = entry.contractor
                    currentOrder["client"] = entry.client
                    currentOrder["service"] = entry.userOrders
                    currentOrder["state"] = entry.status
                    currentOrder["created"] = str(entry.createdWhen)
                    currentOrder["updated"] = str(entry.updatedWhen)
                    currentOrder["chat"] = entry.userCommunication
                    currentOrder["details"] = entry.details
                    currentOrder["files"] = entry.files
                    ordersOfThatCollection.append(currentOrder)
                currentOrderCollection["subOrders"] = ordersOfThatCollection
                output.append(currentOrderCollection)

            # get received orders
            receivedOrders = currentUser.ordersReceived.all()
            # since multiple orders could have been received within the same Order Collection, we need to collect those
            receivedOrdersCollections = {}
            for orderEntry in receivedOrders:
                orderCollection = orderEntry.orderCollectionKey

                if orderCollection.orderCollectionID not in receivedOrdersCollections:
                    receivedOrdersCollections[orderCollection.orderCollectionID] = {"orderID": orderCollection.orderCollectionID, "client": orderCollection.client, "created": str(orderCollection.createdWhen), "updated": str(orderCollection.updatedWhen), "state": orderCollection.status, "subOrders": []}

                currentOrder = {}
                currentOrder["subOrderID"] = orderEntry.orderID
                currentOrder["contractor"] = orderEntry.contractor
                currentOrder["client"] = orderEntry.client
                currentOrder["service"] = orderEntry.userOrders
                currentOrder["state"] = orderEntry.status
                currentOrder["created"] = str(orderEntry.createdWhen)
                currentOrder["updated"] = str(orderEntry.updatedWhen)
                currentOrder["chat"] = orderEntry.userCommunication
                currentOrder["details"] = orderEntry.details
                currentOrder["files"] = orderEntry.files

                receivedOrdersCollections[orderCollection.orderCollectionID]["orders"].append(currentOrder)
            
            # after collection the order collections and their orders, we need to add them to the output
            for orderCollection in receivedOrdersCollections:
                output.append(orderCollection)


            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["date"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output
            #return [result.userOrders, result.orderStatus, result.userCommunication, result.files, result.dates]
        except (Exception) as error:
            print(error)
        
        return []
    
    ##############################################
    @staticmethod
    def getOrdersFlat(session):
        """
        Get all orders for that organisation with little information.

        :param session: session of that user
        :type session: dict
        :return: sorted list 
        :rtype: list

        """
        try:
            # get organisation
            currentUser = Organization.objects.get(subID=session["user"]["userinfo"]["org_id"])
            orderCollections = currentUser.ordersSubmitted.all()

            # get associated OrderCollections for submitted orders
            output = []
            
            for orderCollection in orderCollections:
                currentOrderCollection = {}
                currentOrderCollection["orderID"] = orderCollection.orderCollectionID
                currentOrderCollection["created"] = str(orderCollection.createdWhen)
                currentOrderCollection["updated"] = str(orderCollection.updatedWhen)
                currentOrderCollection["state"] = orderCollection.status
                currentOrderCollection["client"] = orderCollection.client
                currentOrderCollection["subOrderCount"] = len(list(orderCollection.orders.all()))

                output.append(currentOrderCollection)

            # get received orders
            receivedOrders = currentUser.ordersReceived.all()
            # since multiple orders could have been received within the same Order Collection, we need to collect those
            receivedOrdersCollections = {}
            for orderEntry in receivedOrders:
                orderCollection = orderEntry.orderCollectionKey

                if orderCollection.orderCollectionID not in receivedOrdersCollections:
                    receivedOrdersCollections[orderCollection.orderCollectionID] = {"orderID": orderCollection.orderCollectionID, "client": orderCollection.client, "created": str(orderCollection.createdWhen), "updated": str(orderCollection.updatedWhen), "state": orderCollection.status, "subOrderCount": 0}
                receivedOrdersCollections[orderCollection.orderCollectionID]["subOrderCount"] += 1
            
            # after collection the order collections and their orders, we need to add them to the output
            for orderCollection in receivedOrdersCollections:
                output.append(orderCollection)


            output = sorted(output, key=lambda x: 
                   timezone.make_aware(datetime.strptime(x["date"], '%Y-%m-%d %H:%M:%S.%f+00:00')), reverse=True)
            return output
            #return [result.userOrders, result.orderStatus, result.userCommunication, result.files, result.dates]
        except (Exception) as error:
            print(error)
        
        return []
    

pgOBase = OrderManagementBase()
pgOUser = OrderManagementUser()
pgOOrganization = OrderManagementOrganization()