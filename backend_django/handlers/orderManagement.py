"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers managing the orders
"""

import json, random, logging
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ..services.postgresDB import pgProfiles, pgOrders

from ..handlers.basics import checkIfUserIsLoggedIn, checkIfRightsAreSufficient, manualCheckifLoggedIn, manualCheckIfRightsAreSufficient

from ..services import redis, crypto, rights
from ..services.processes import price, collectAndSend

logger = logging.getLogger(__name__)
################################################################################################
# order collections aka orders

#######################################################
@require_http_methods(["GET"])
def createOrderCollectionID(request):
    """
    Create order collection ID for frontend

    :param request: GET Request
    :type request: HTTP GET
    :return: order collection ID as string
    :rtype: JSONResponse

    """
    # generate ID string, make timestamp and create template for order collection
    orderCollectionID = crypto.generateURLFriendlyRandomString()
    now = timezone.now()

    # login defines client
    if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, "createOrderCollectionID"):
        template = {"orderID": orderCollectionID, "client": pgProfiles.profileManagement[request.session["pgProfileClass"]].getClientID(request.session), "state": 0, "created": str(now), "updated": str(now), "details": {}, "subOrders": {}} 
    else:
        template = {"orderID": orderCollectionID, "client": "", "state": 0, "created": str(now), "updated": str(now), "details": {}, "subOrders": {}} 
    
    # save order collection template in session for now
    if "currentOrder" not in request.session:
        request.session["currentOrder"] = {}
    request.session["currentOrder"][orderCollectionID] = template
    request.session.modified = True

    #return just the id for the frontend
    return JsonResponse({"orderID": orderCollectionID})

#######################################################
@require_http_methods(["PATCH"])
def updateOrderCollection(request):
    """
    Update stuff about the order collection

    :param request: Request with content
    :type request: HTTP PATCH
    :return: Message if it worked or not
    :rtype: HTTPResponse

    """
    try:
        changes = json.loads(request.body.decode("utf-8"))
        orderCollectionID = changes["orderID"]

        if "currentOrder" in request.session and orderCollectionID in request.session["currentOrder"]:
            if "state" in changes["changes"]:
                request.session["currentOrder"][orderCollectionID]["state"] = changes["changes"]["state"]
            elif "details" in changes["changes"]:
                for elem in changes["changes"]["details"]:
                    request.session["currentOrder"][orderCollectionID]["details"][elem] = changes["changes"]["details"][elem]
            request.session.modified = True
        else:
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, "updateOrderCollection"):
                if "state" in changes["changes"]:
                    returnVal = pgOrders.OrderManagementBase.updateOrderCollection(orderCollectionID, pgOrders.EnumUpdates.status, changes["changes"]["state"])
                    if isinstance(returnVal, Exception):
                        raise returnVal
                if "details" in changes["changes"]:
                    returnVal = pgOrders.OrderManagementBase.updateOrderCollection(orderCollectionID, pgOrders.EnumUpdates.details, changes["changes"]["details"])
                    if isinstance(returnVal, Exception):
                        raise returnVal
                
                # TODO send to websockets that are active, that a new message/status is available for that order
                # outputDict = {"eventType": "orderEvent"}
                # outputDict["orderID"] = orderCollectionID
                # outputDict["orders"] = [{"orderID": orderID, "status": 1, "messages": 0}]
                # channel_layer = get_channel_layer()
                # listOfUsers = pgOrders.OrderManagementBase.getAllUsersOfOrder(orderID)
                # for user in listOfUsers:
                #     if user.subID != pgProfiles.ProfileManagementBase.getUserKey(session=request.session):
                #         async_to_sync(channel_layer.group_send)(pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=user.subID), {
                #             "type": "sendMessageJSON",
                #             "dict": outputDict,
                #         })
                logger.info(f"{pgProfiles.ProfileManagementBase.getUser(request.session)['name']} updated order {orderCollectionID} at " + str(datetime.now()))

            else:
                return HttpResponse("Not logged in", status=401)

        return HttpResponse("Success")
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed",status=500)

#######################################################
@require_http_methods(["DELETE"])
def deleteOrderCollection(request, orderCollectionID):
    """
    Delete the whole order collection

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param orderCollectionID: id of the order collection
    :type orderCollectionID: str
    :return: Success or not
    :rtype: HTTPRespone

    """
    try:
        if "currentOrder" in request.session and orderCollectionID in request.session["currentOrder"]:
            del request.session["currentOrder"][orderCollectionID]
            request.session.modified = True

        elif manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, "deleteOrderCollection"):
            pgOrders.OrderManagementBase.deleteOrderCollection(orderCollectionID)
        else:
            raise Exception("Not logged in or rights insufficient!")

        return HttpResponse("Success")
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed",status=500)
################################################################################################
# orders aka subOrders

#######################################################
@require_http_methods(["GET"])
def createOrderID(request, orderCollectionID):
    """
    Create order ID for frontend

    :param request: GET Request
    :type request: HTTP GET
    :param orderCollectionID: id of the order collection the created order should belong to
    :type orderCollectionID: str
    :return: order ID as string
    :rtype: JSONResponse

    """
    try:
        # generate ID, timestamp and template for sub order
        orderID = crypto.generateURLFriendlyRandomString()
        now = timezone.now()
        template = {"subOrderID": orderID, "contractor": [], "state": 0, "created": str(now), "updated": str(now), "files": {"files" : []}, "details": {}, "chat": {"messages": []}, "service": {}}

        # save into respective order collection
        if "currentOrder" in request.session and orderCollectionID in request.session["currentOrder"]:
            request.session["currentOrder"][orderCollectionID]["subOrders"][orderID] = template
            request.session.modified = True
            return JsonResponse({"subOrderID": orderID})

        # else: it's in the database, fetch it from there
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, "createOrderID"):
            returnObj = pgOrders.OrderManagementBase.addOrderTemplateToCollection(orderCollectionID, template, pgProfiles.profileManagement[request.session["pgProfileClass"]].getClientID(request.session))
            if isinstance(returnObj, Exception):
                raise returnObj

        # return just the generated ID for frontend
        return JsonResponse({"subOrderID": orderID})
    except (Exception) as error:
        print(error)
        return JsonResponse({}, status=500)

#######################################################
@require_http_methods(["PATCH"])
def updateOrder(request):
    """
    Update stuff about the order

    :param request: Request with content
    :type request: HTTP PATCH
    :return: Message if it worked or not
    :rtype: HTTPResponse

    """
    try:
        now = timezone.now()
        changes = json.loads(request.body.decode("utf-8"))
        orderCollectionID = changes["orderID"]
        orderID = changes["subOrderID"]
        if "currentOrder" in request.session and orderCollectionID in request.session["currentOrder"]:
            # changes
            for elem in changes["changes"]:
                if elem == "service": # service is a dict in itself
                    if "type" in changes["changes"]["service"] and changes["changes"]["service"]["type"] == 0:
                            request.session["currentOrder"][orderCollectionID]["subOrders"][orderID] = {"subOrderID": orderID, "contractor": [], "state": 0, "created": str(now), "updated": str(now), "files": {"files" : []}, "details": {}, "chat": {"messages": []}, "service": {}}
                    else:
                        for entry in changes["changes"]["service"]:
                            request.session["currentOrder"][orderCollectionID]["subOrders"][orderID]["service"][entry] = changes["changes"]["service"][entry]
                elif elem == "chat":
                    request.session["currentOrder"][orderCollectionID]["subOrders"][orderID]["chat"]["messages"].append(changes["changes"]["chat"])
                elif elem == "files":
                    request.session["currentOrder"][orderCollectionID]["subOrders"][orderID]["files"]["files"] = changes["changes"]["files"]
                    # state, contractor
                elif elem == "details":
                    for entry in changes["changes"]["details"]:
                        request.session["currentOrder"][orderCollectionID]["subOrders"][orderID]["details"][entry] = changes["changes"]["details"][entry]
                else:
                    request.session["currentOrder"][orderCollectionID]["subOrders"][orderID][elem] = changes["changes"][elem]
            # deletions
            if "deletions" in changes:
                for elem in changes["deletions"]:
                    if len(changes["deletions"][elem]) > 0:
                        for entry in changes["deletions"][elem]:
                            del request.session["currentOrder"][orderCollectionID]["subOrders"][orderID][elem][entry]
                    else:
                        del request.session["currentOrder"][orderCollectionID]["subOrders"][orderID][elem]
            
            request.session["currentOrder"][orderCollectionID]["subOrders"][orderID]["updated"] = str(now)
            request.session.modified = True
        else:
            # database version
            if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, "updateOrder"):
                for elem in changes["changes"]:
                    returnVal = True
                    if elem == "service": # service is a dict in itself
                        if "type" in changes["changes"]["service"] and changes["changes"]["service"]["type"] == 0:
                            returnVal = pgOrders.OrderManagementBase.updateOrder(orderID, pgOrders.EnumUpdates.service, {})
                        else:        
                            returnVal = pgOrders.OrderManagementBase.updateOrder(orderID, pgOrders.EnumUpdates.service, changes["changes"]["service"])
                    elif elem == "chat":
                        returnVal = pgOrders.OrderManagementBase.updateOrder(orderID, pgOrders.EnumUpdates.chat, changes["changes"]["chat"])
                    elif elem == "files":
                        returnVal = pgOrders.OrderManagementBase.updateOrder(orderID, pgOrders.EnumUpdates.files, changes["changes"]["files"])
                    elif elem == "contractor":
                        returnVal = pgOrders.OrderManagementBase.updateOrder(orderID, pgOrders.EnumUpdates.contractor, changes["changes"]["contractor"])
                    elif elem == "details":
                        returnVal = pgOrders.OrderManagementBase.updateOrder(orderID, pgOrders.EnumUpdates.details, changes["changes"]["details"])
                    else:
                        # state
                        returnVal = pgOrders.OrderManagementBase.updateOrder(orderID, pgOrders.EnumUpdates.status, changes["changes"]["state"])

                    if isinstance(returnVal, Exception):
                        raise returnVal
                if "deletions" in changes:
                    for elem in changes["deletions"]:
                        returnVal = True
                        if elem == "service": # service is a dict in itself      
                            returnVal = pgOrders.OrderManagementBase.deleteFromOrder(orderID, pgOrders.EnumUpdates.service, changes["deletions"]["service"])
                        elif elem == "chat":
                            returnVal = pgOrders.OrderManagementBase.deleteFromOrder(orderID, pgOrders.EnumUpdates.chat, changes["deletions"]["chat"])
                        elif elem == "files":
                            returnVal = pgOrders.OrderManagementBase.deleteFromOrder(orderID, pgOrders.EnumUpdates.files, changes["deletions"]["files"])
                        elif elem == "contractor":
                            returnVal = pgOrders.OrderManagementBase.deleteFromOrder(orderID, pgOrders.EnumUpdates.contractor, changes["deletions"]["contractor"])
                        elif elem == "details":
                            returnVal = pgOrders.OrderManagementBase.deleteFromOrder(orderID, pgOrders.EnumUpdates.details, changes["deletions"]["details"])
                        else:
                            # state
                            returnVal = pgOrders.OrderManagementBase.deleteFromOrder(orderID, pgOrders.EnumUpdates.status, changes["deletions"]["state"])

                        if isinstance(returnVal, Exception):
                            raise returnVal
                
                # websocket
                dictForEvents = pgOrders.OrderManagementBase.getInfoAboutOrderForWebsocket(orderCollectionID)
                channel_layer = get_channel_layer()
                for userID in dictForEvents: # user/orga that is associated with that order
                    values = dictForEvents[userID] # message, formatted for frontend
                    subID = pgProfiles.ProfileManagementBase.getUserKeyViaHash(userID) # primary key
                    if userID != pgProfiles.ProfileManagementBase.getUserKey(session=request.session): # don't show a message for the user that changed it
                        userKeyWOSC = pgProfiles.ProfileManagementBase.getUserKeyWOSC(uID=subID)
                        for permission in rights.rightsManagement.getPermissionsNeededForPath("updateOrder"):
                            async_to_sync(channel_layer.group_send)(userKeyWOSC+permission, {
                                "type": "sendMessageJSON",
                                "dict": values,
                            })
                logger.info(f"{pgProfiles.ProfileManagementBase.getUser(request.session)['name']} updated subOrder {orderID} at " + str(datetime.now()))

            else:
                return HttpResponse("Not logged in", status=401)

        return HttpResponse("Success")
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed",status=500)

#######################################################
@require_http_methods(["DELETE"])
def deleteOrder(request, orderCollectionID, orderID):
    """
    Delete one order

    :param request: DELETE Request
    :type request: HTTP DELETE
    :param orderCollectionID: id of the order collection
    :type orderCollectionID: str
    :param orderID: id of the order
    :type orderID: str
    :return: Success or not
    :rtype: HTTPRespone

    """
    try:
        if "currentOrder" in request.session and orderCollectionID in request.session["currentOrder"]:
            del request.session["currentOrder"][orderCollectionID]["subOrders"][orderID]
            request.session.modified = True

        elif manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, "deleteOrder"):
            pgOrders.OrderManagementBase.deleteOrder(orderID)
        else:
            raise Exception("Not logged in or rights insufficient!")
        
        return HttpResponse("Success")
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed",status=500)

################################################################################################
# retrieval

#######################################################
@require_http_methods(["GET"]) 
def getFlatOrders(request):
    """
    Retrieve orders without much detail.

    :param request: GET Request
    :type request: HTTP GET
    :return: Response with list
    :rtype: JSON Response

    """
    try:
        outDict = {"orders": []}
        # From session
        if "currentOrder" in request.session:
            for entry in request.session["currentOrder"]:
                tempDict = {}
                tempDict["orderID"] = request.session["currentOrder"][entry]["orderID"]
                tempDict["client"] = request.session["currentOrder"][entry]["client"]
                tempDict["state"] =  request.session["currentOrder"][entry]["state"]
                tempDict["created"] = request.session["currentOrder"][entry]["created"]
                tempDict["updated"] = request.session["currentOrder"][entry]["updated"]
                tempDict["details"] = request.session["currentOrder"][entry]["details"]
                tempDict["subOrderCount"] = len(request.session["currentOrder"][entry]["subOrders"])
                outDict["orders"].append(tempDict)
        
        # From Database
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, "getFlatOrders"):
            objFromDB = pgOrders.orderManagement[request.session["pgOrderClass"]].getOrdersFlat(request.session)
            if len(objFromDB) >= 1:
                outDict["orders"].extend(objFromDB)

        return JsonResponse(outDict)
    
    except (Exception) as error:
        print(error)
        
    return JsonResponse({"orders": []})

#######################################################
@require_http_methods(["GET"]) 
def getOrder(request, orderCollectionID):
    """
    Retrieve order collection and orders.

    :param request: GET Request
    :type request: HTTP GET
    :param orderCollectionID: id of the order collection
    :type orderCollectionID: str
    :return: Response with dict
    :rtype: JSON Response

    """
    try:
        outDict = {}
        if "currentOrder" in request.session:
            if orderCollectionID in request.session["currentOrder"]:
                outDict["orderID"] = request.session["currentOrder"][orderCollectionID]["orderID"]
                outDict["client"] = request.session["currentOrder"][orderCollectionID]["client"]
                outDict["state"] =  request.session["currentOrder"][orderCollectionID]["state"]
                outDict["created"] = request.session["currentOrder"][orderCollectionID]["created"]
                outDict["updated"] = request.session["currentOrder"][orderCollectionID]["updated"]
                outDict["details"] = request.session["currentOrder"][orderCollectionID]["details"]
                outDict["subOrders"] = []
                for elem in request.session["currentOrder"][orderCollectionID]["subOrders"]:
                    outDict["subOrders"].append(request.session["currentOrder"][orderCollectionID]["subOrders"][elem])
                return JsonResponse(outDict)
        
        if manualCheckifLoggedIn(request.session) and manualCheckIfRightsAreSufficient(request.session, "getOrder"):
            return JsonResponse(pgOrders.OrderManagementBase.getOrderCollection(orderCollectionID))

        return JsonResponse(outDict)
    except (Exception) as error:
            print(error)
    return JsonResponse({})

#######################################################
@checkIfUserIsLoggedIn()
@checkIfRightsAreSufficient(json=True)
def retrieveOrders(request):
    """
    Retrieve all saved orders.

    :param request: GET Request
    :type request: HTTP GET
    :return: JSON Response with orders of that user
    :rtype: JSON Response

    """

    return JsonResponse(pgOrders.orderManagement[request.session["pgOrderClass"]].getOrders(request.session), safe=False)
    

#######################################################
@checkIfUserIsLoggedIn(json=True)
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def getMissedEvents(request):
    """
    Show how many events (chat messages ...) were missed since last login.

    :param request: GET Request
    :type request: HTTP GETF
    :return: JSON Response with numbers for every order and orderCollection
    :rtype: JSON Response

    """

    user = pgProfiles.ProfileManagementBase.getUser(request.session)
    lastLogin = user["lastSeen"]
    orderCollections = pgOrders.orderManagement[request.session["pgOrderClass"]].getOrders(request.session)

    output = {"eventType": "orderEvent", "events": []}

    for orderCollection in orderCollections:
        currentCollection = {}
        currentCollection["orderCollectionID"] = orderCollection["orderID"]
        orderArray = []
        for orders in orderCollection["subOrders"]:
            currentOrder = {}
            currentOrder["orderID"] = orders["subOrderID"]
            newMessagesCount = 0
            chat = orders["chat"]["messages"]
            for messages in chat:
                if lastLogin < timezone.make_aware(datetime.strptime(messages["date"], '%Y-%m-%d %H:%M:%S.%f+00:00')) and messages["userID"] != user["hashedID"]:
                    newMessagesCount += 1
            if lastLogin < timezone.make_aware(datetime.strptime(orders["updated"], '%Y-%m-%d %H:%M:%S.%f+00:00')):
                status = 1
            else:
                status = 0
            
            # if something changed, save it. If not, discard
            if status !=0 or newMessagesCount != 0: 
                currentOrder["status"] = status
                currentOrder["messages"] = newMessagesCount

                orderArray.append(currentOrder)
        if len(orderArray):
            currentCollection["orders"] = orderArray
            output["events"].append(currentCollection)
    
    # set accessed time to now
    pgProfiles.ProfileManagementBase.setLoginTime(user["hashedID"])

    return JsonResponse(output, status=200, safe=False)

################################################################################################
# Save, verify, send

##############################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"])
@checkIfRightsAreSufficient(json=True)
def getManufacturers(request):
    """
    Get all suitable manufacturers.

    :param request: GET request
    :type request: HTTP GET
    :return: List of manufacturers and some details
    :rtype: JSON

    """

    manufacturerList = []
    listOfAllManufacturers = pgProfiles.ProfileManagementOrganization.getAllManufacturers()
    # TODO Check suitability

    # remove unnecessary information and add identifier
    for idx, elem in enumerate(listOfAllManufacturers):
        manufacturerList.append({})
        manufacturerList[idx]["name"] = elem["name"]
        manufacturerList[idx]["id"] = elem["hashedID"]

    return JsonResponse(manufacturerList, safe=False)

#######################################################
def saveOrderViaWebsocket(session):
    """
    Save order in database

    :param session: session of user
    :type session: Dict
    :return: None
    :rtype: None

    """
    try:
        if manualCheckifLoggedIn(session) and manualCheckIfRightsAreSufficient(session, "saveOrder"):
            if session["isPartOfOrganization"]:
                error = pgOrders.OrderManagementOrganization.addOrderToDatabase(session)
            else:
                error = pgOrders.OrderManagementUser.addOrderToDatabase(session)
            if isinstance(error, Exception):
                raise error
            logger.info(f"{pgProfiles.ProfileManagementBase.getUser(session)['name']} saved their order at " + str(datetime.now()))
        return None
    
    except (Exception) as error:
        print(error)
        return error

#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["GET"]) 
@checkIfRightsAreSufficient(json=False)
def saveOrder(request):
    """
    Save order in database

    :param request: GET Request
    :type request: HTTP GET
    :return: Response if sent successfully or not
    :rtype: HTTP Response

    """

    try:
        # TODO Save picture and files in permanent storage, and change "files" field to urls

        if request.session["isPartOfOrganization"]:
            error = pgOrders.OrderManagementOrganization.addOrderToDatabase(request.session)
        else:
            error = pgOrders.OrderManagementUser.addOrderToDatabase(request.session)
        if isinstance(error, Exception):
            raise error

        logger.info(f"{pgProfiles.ProfileManagementBase.getUser(request.session)['name']} saved their order at " + str(datetime.now()))
        return HttpResponse("Success")
    
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed")
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"]) 
@checkIfRightsAreSufficient(json=False)
def verifyOrder(request):
    """
    Start calculations on server and set status accordingly

    :param request: GET Request
    :type request: HTTP GET
    :return: Response if processes are started successfully
    :rtype: HTTP Response

    """
    try:
        # get information
        info = json.loads(request.body.decode("utf-8"))
        orderID = info["orderID"]
        sendToManufacturerAfterVerification = info["send"]
        subOrderIDArray = info["subOrderIDs"]

        # TODO start services and set status to "verifying"
        listOfCallIDsAndOrderIDs = []
        for entry in subOrderIDArray:
            pgOrders.OrderManagementBase.updateOrder(entry, pgOrders.EnumUpdates.status, 400)
            call = price.calculatePrice_Mock.delay([1,2,3]) # placeholder for each thing like model, material, post-processing
            listOfCallIDsAndOrderIDs.append((call.id, entry, collectAndSend.EnumResultType.price))

        # start collecting process, 
        collectAndSend.waitForResultAndSendOrder(listOfCallIDsAndOrderIDs, sendToManufacturerAfterVerification)

        # TODO Websocket Event

        logger.info(f"{pgProfiles.ProfileManagementBase.getUser(request.session)['name']} wants to verify their order at " + str(datetime.now()))

        return HttpResponse("Success")
    
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed")
    
#######################################################
@checkIfUserIsLoggedIn()
@require_http_methods(["PATCH"]) 
@checkIfRightsAreSufficient(json=False)
def sendOrder(request):
    """
    Retrieve Calculations and send order to manufacturer(s)

    :param request: GET Request
    :type request: HTTP GET
    :return: Response if processes are started successfully
    :rtype: HTTP Response

    """
    try:
        info = json.loads(request.body.decode("utf-8"))
        orderID = info["orderID"]
        subOrderIDArray = info["subOrderIDs"]
        # TODO Check if order is verified

        # TODO send to manufacturer(s))
        # TODO set status to send/requested 600
        # TODO Websocket Events
        logger.info(f"{pgProfiles.ProfileManagementBase.getUser(request.session)['name']} sent their order at " + str(datetime.now()))
        
        return HttpResponse("Success")
    
    except (Exception) as error:
        print(error)
        return HttpResponse("Failed")
