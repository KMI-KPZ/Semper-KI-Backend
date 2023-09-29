"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Collect result, set state and send order
"""
import enum, time

from ...celery import app
from celery.result import AsyncResult 

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
    # outputObject (JSON)
    output = {}
    for entry in listOfIDsAndOrderIDs:
        result = AsyncResult(entry[0])
        while result.state != "SUCCESS" or result.state != "FAILURE":
            # sleep as to not keep the cpu unecessarily busy
            time.sleep(5)
            continue
        if result.state == "SUCCESS":

            # Save results
            if entry[2] == EnumResultType.price:
                summedUpPrice, individualPrices = result.get()
                output["prices"] = {"sum": summedUpPrice, "individual": individualPrices}
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
    # TODO Set status to VERIFIED

    return output
    
    

