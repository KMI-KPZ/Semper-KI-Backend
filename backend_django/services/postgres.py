"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for database calls
"""
import types

from django.utils import timezone

from ..modelFiles.profile import Profile
from ..modelFiles.orders import Orders

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
            obj = Profile.objects.get(subID=userID).toDict()
        except (Exception) as error:
            print(error)

        return obj
    
    ##############################################
    @staticmethod
    def getUserID(session):
        """
        Retrieve User ID from Session

        :param session: session
        :type session: Dictionary
        :return: User details from database
        :rtype: Dictionary

        """
        userID = ""
        try:
            userID = session["user"]["userinfo"]["sub"]
        except (Exception) as error:
            print(error)

        return userID
    
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
        userType = session["usertype"]
        updated = timezone.now()
        try:
            # first get, then create
            result = Profile.objects.get(subID=userID)
            if result.role != userType:
                Profile.objects.filter(subID=userID).update(role=userType)
        except (Exception) as error:
            try:
                Profile.objects.create(subID=userID, name=userName, email=userEmail, role=userType, updatedWhen=updated) 
            except (Exception) as error:
                print(error)
                return False
            pass
        return True

    ##############################################
    @staticmethod
    def updateRole(session):
        """
        Update user role.

        :param session: GET request session
        :type session: Dictionary
        :return: Flag if it worked or not
        :rtype: Bool

        """
        userID = session["user"]["userinfo"]["sub"]
        userType = session["usertype"]
        if userType == "admin": # disallow admin
            print("Getting to be an admin this way is not allowed!")
            return False

        updated = timezone.now()
        try:
            affected = Profile.objects.filter(subID=userID).update(role=userType, updatedWhen=updated)
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
            affected = Profile.objects.filter(subID=userID).delete()
        except (Exception) as error:
            print(error)
            return False
        return True

####################################################################################
# Orders
class OrderManagement():
    ##############################################
    @staticmethod
    def addOrder(userID, orderID, orderFromUser):
        """
        Add order for that user. Check if user already has orders and append if so, create a new user if not.

        :param userID: user ID of a user as primary key
        :type userID: str
        :param orderID: unique order ID
        :type orderID: str
        :param orderFromUser: order details
        :type orderFromUser: json dict
        :return: Flag if it worked or not
        :rtype: Bool

        """

        now = timezone.now()
        try:
            # first get
            result = Orders.objects.get(uID=userID)
            # user exists but are there orders?
            if len(result.orderIDs):
                result.orderIDs.append(orderID)
                result.userOrders[orderID] = orderFromUser
                result.orderStatus[orderID] = {}
                result.userCommunication[orderID] = {}
                result.files[orderID] = []
                result.dates[orderID] = {"created": str(now), "updated": str(now)}
                Orders.objects.filter(uID=userID).update(orderIDs=result.orderIDs, userOrders=result.userOrders, orderStatus=result.orderStatus, userCommunication=result.userCommunication, dates=result.dates, updatedWhen=now)
        except (Exception) as error:
            # user doesn't exist
            try:
                Orders.objects.create(uID=userID, orderIDs=[orderID], userOrders={orderID: orderFromUser}, orderStatus={orderID: {}}, userCommunication={orderID: {}}, files={orderID: []}, dates={orderID: {"created": str(now), "updated": str(now)}}, updatedWhen=now) 
            except (Exception) as error:
                print(error)
                return False
            pass
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
            result = Orders.objects.get(uID=userID)
            return [result.userOrders, result.orderStatus, result.userCommunication, result.files, result.dates]
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
            result = Orders.objects.get(uID=userID)
            result.orderIDs.remove(orderID)
            result.userOrders.pop(orderID)
            result.orderStatus.pop(orderID)
            result.userCommunication.pop(orderID)
            result.files.pop(orderID)
            result.dates.pop(orderID)
            Orders.objects.filter(uID=userID).update(orderIDs=result.orderIDs, userOrders=result.userOrders, orderStatus=result.orderStatus, userCommunication=result.userCommunication, files=result.files, updatedWhen=updated)
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
            result = Orders.objects.get(uID=userID)
            # edit one after another
            result.dates[orderID]["updated"] = str(updated)
            if orderFromUser != {}:
                result.userOrders[orderID] = orderFromUser
                Orders.objects.filter(uID=userID).update(userOrders=result.userOrders, dates=result.dates, updatedWhen=updated)
            if orderStatus != {}:
                result.orderStatus[orderID] = orderStatus
                Orders.objects.filter(uID=userID).update(orderStatus=result.orderStatus, dates=result.dates, updatedWhen=updated)
            if userCommunications != {}:
                result.userCommunication[orderID] = userCommunications
                Orders.objects.filter(uID=userID).update(userCommunication=result.userCommunication, dates=result.dates, updatedWhen=updated)
            if files != {}:
                result.files[orderID] = files
                Orders.objects.filter(uID=userID).update(files=result.files, dates=result.dates, updatedWhen=updated)
            return True
        except (Exception) as error:
            print(error)
        return False