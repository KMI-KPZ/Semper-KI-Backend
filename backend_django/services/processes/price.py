"""
Part of Semper-KI software

Silvio Weging 2023

Contains: BS Calculation of the price
"""

import  random
from ...celery import app

################################################################################################
#######################################################
@app.task
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

