"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Interface with the message queuing system
"""
import code_SemperKI.utilities.asyncTask as aTask
import MSQ.module.celery as TaskQueue
from ..tasks.tasks import dummy, dummyDerp
from django.http import HttpResponse

####################################################################
# Remote stuff 

####################################################################
def getResultsBack(request, taskID):
    """
    Send example script to remote worker
    
    :param request: Get request, not used
    :type request: GET
    :param taskID: The task ID as GET Parameter sent from the remote worker
    :type taskID: str
    :return: Response which is not awaited
    :rtype: HttpResponse
    """
    retVal = TaskQueue.app.AsyncResult(taskID)
    print(retVal.result)
    return HttpResponse("Success")

####################################################################
def sendExampleRemote(request):
    """
    Send example script to remote worker
    
    """
    retVal = TaskQueue.app.send_task(name="runScript", args=[open("MSQ/scripts/test.py").read(),(1,"bla")], queue="remote")
    return HttpResponse("Success")

@aTask.runInBackground
def derp(a,b):
    print("Task done", a)
    return str(a)+b

####################################################################
def sendExampleLocal(request):
    """
    Send example script to remote worker
    
    """
    #retVal = dummy.delay(1,"bla")
    #retVal = dummyDerp.delay(1,"bla")
    derp(1,"bla")
    derp(2,"bla")
    derp(3,"bla")
    derp(4,"bla")
    print("Success")
    return HttpResponse("Success")