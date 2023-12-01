"""
Part of Semper-KI software

Silvio Weging 2023

Contains: BS Calculation of the price
"""

import  random
# from ...celery import app
# from celery.result import AsyncResult

################################################################################################
#######################################################
# @app.task
def calculatePrice_Mock(items):
    """
    Random prices calculation
    """
    summedUpPrices= 0
    priceForEach = []
    for idx, elem in enumerate(items):
        price = random.randint(1,100)
        summedUpPrices += price
        priceForEach.append(price)
    
    return summedUpPrices, priceForEach

#######################################################
def getResults(id):
    """
    Return results via ID
    """

    result = AsyncResult(id, app=app)
    if result.state == 'SUCCESS':
        return result.get()
    if result.state == 'FAILURE':
        return Exception("Job failed")
    return None # job is not finished yet
    