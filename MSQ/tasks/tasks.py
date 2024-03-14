from ..module.celery import app

####################################################################
@app.task
def dummy(a:int,b:str):
    return str(a)+b

####################################################################
@app.task
def dummyDerp(a:int,b:str):
    return str(a)+b