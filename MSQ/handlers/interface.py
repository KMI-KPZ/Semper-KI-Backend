"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Interface with the message queuing system
"""
from Generic_Backend.code_General.connections import s3
import MSQ.module.celery as TaskQueue
from ..tasks.tasks import dummy, callfTetWild
from django.http import FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from code_SemperKI.utilities.basics import *
from rest_framework.decorators import api_view
from code_SemperKI.utilities.serializer import ExceptionSerializer

####################################################################
def returnFileFromfTetWild(filePath:str):
    """
    Only temporary solution

    """
    content, flag = s3.manageLocalS3.downloadFile(filePath)
    if flag is False:
        content, flag = s3.manageRemoteS3.downloadFile(filePath)
        if flag is False:
            return HttpResponse("Not found", status=404)
    return FileResponse(content, filename="Test.ugrid")

#########################################################################
# getResultsBack
#"getResultsBackLocal": ("private/getResultsLocal/<str:taskID>/", interface.getResultsBack)
#########################################################################
#TODO Add serializer for getResultsBack
#########################################################################
# Handler  
@extend_schema(
    summary="Get results from celery worker via ID, dispatch to further handlers",
    description=" ",
    tags=['celery'],
    request=None,
    responses={
        200: None,
        401: ExceptionSerializer,
        500: ExceptionSerializer
    }
)
# @checkIfUserIsLoggedIn()
# @require_http_methods(["GET"])
# @checkIfRightsAreSufficient(json=False)
@api_view(["GET"])
def getResultsBack(request, taskID):
    """
    Get results from celery worker via ID, dispatch to further handlers
    
    :param request: Get request, not used
    :type request: GET
    :param taskID: The task ID as GET Parameter sent from the remote worker
    :type taskID: str
    :return: Response which is not awaited
    :rtype: HttpResponse
    """
    retVal = TaskQueue.app.AsyncResult(taskID)
    callingFunction = retVal.result[1]
    resultOfCalculation = retVal.result[0]
    if callingFunction == dummy.__name__:
        return HttpResponse(retVal.result)
    elif callingFunction == callfTetWild.__name__:
        return returnFileFromfTetWild(resultOfCalculation)
    return HttpResponse("Success")

####################################################################
# def sendExampleRemote(request):
#     """
#     Send example script to remote worker
    
#     """
#     retVal = TaskQueue.app.send_task(name="runScript", args=[open("MSQ/scripts/test.py").read(),(1,"bla")], queue="remote")
#     return HttpResponse("Success")

####################################################################
from io import BytesIO
def sendExampleLocal(request):
    """
    Send example to worker
    
    """
    retVal = dummy.delay(1,"bla")
    return HttpResponse("Success")