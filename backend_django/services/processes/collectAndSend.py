"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Collect result, set state and send order
"""
import enum

from ...celery import app
from celery.result import AsyncResult

from ..postgresDB import pgOrders 

################################################################################################
class EnumResultType(enum.Enum):
    price = 1
    logistics = 2
    printability = 3

#######################################################

def waitForResultAndSendOrder(listOfIDsAndOrderIDs: list, sendOrder: bool):
    """
    Await all IDs from list, set status of orders and call sendOrder
    """
    for entry in listOfIDsAndOrderIDs:
        result = AsyncResult(entry[0])
        while result.state != "SUCCESS" or result.state != "FAILURE":
            # sleep
            continue
        if result.state == "SUCCESS":
            # Set Status 
            pgOrders.OrderManagementBase.updateOrder(entry[1], pgOrders.EnumUpdates.status, 500)
            # Save results
            if entry[2] == EnumResultType.price:
                summedUpPrice, individualPrices = result.get()
                pgOrders.OrderManagementBase.updateOrder(entry[1], pgOrders.EnumUpdates.service, {"prices": {"sum": summedUpPrice, "individual": individualPrices}})
            elif entry[2] == EnumResultType.logistics:
                resultOfCalculation = result.get()
                pass
            elif entry[2] == EnumResultType.printability:
                resultOfCalculation = result.get()
                pass
            
            pass
        else: # FAILED
            # TODO 
            pass
    if sendOrder:
        # TODO Call send
        pass
    # Don't send
    
    

