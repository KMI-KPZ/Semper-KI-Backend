"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Views for some backend websites
"""
from multiprocessing.pool import AsyncResult
import threading

from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

from django.http import HttpResponse
from django.shortcuts import render
import requests
import json
import time
from django.utils.decorators import sync_and_async_middleware
from requeststest import CeleryTaskManager

from backend_django.services.auth0 import authorizeToken
##########################################################

def landingPage(request):
    print("landingpage")
    # print thread id
    print('landing page in thread: '+ str(threading.get_ident()))
    # data = {
    # "args": [4, 2]
    #  }
    # task_start = CeleryTaskManager(taskname='trialtask', data=data,)
    # result = task_start.check_status()
    return render(
        request,
        "landingPage.html",
        # context={
        #     'result':result,
        #}
    )

#######################################################
def benchyPage(request):
    """
    Landing page for the benchmark tool

    :param request: GET request
    :type request: HTTP GET
    :return: Rendered page
    :rtype: None

    """
    return render(
        request,
        "benchy.html"#,
        #context={
        #    "session": request.session.get("user"),
            #"pretty": json.dumps(request.session.get("user"), indent=4),
        #},
    )

#######################################################
def docPage(request):
    """
    Documentation page for the backend

    :param request: GET request
    :type request: HTTP GET
    :return: Rendered page
    :rtype: None

    """
    #response = HttpResponse()
    # construct the file's path
    #url=os.path.join(settings.BASE_DIR,'doc','build','html','index.html')
    #response['Content-Type']=""
    #response['X-Accel-Redirect'] = url
    #return response
    pathOfHtml = request.path.replace('public/doc/', '').replace('index.html', '')
    print(pathOfHtml)
    if ("_static" in pathOfHtml):
        return render(
        request,
        settings.DOC_DIR + pathOfHtml)
    else:
        return render(
            request,
            settings.DOC_DIR + pathOfHtml + "index.html"
        )

#######################################################
def sparqlPage(request):
    """
    Landing page for a sparql test query

    :param request: GET request
    :type request: HTTP GET
    :return: Rendered page
    :rtype: None

    """
    return render(
        request,
        "sparql.html"#,
        #context={
        #    "session": request.session.get("user"),
            #"pretty": json.dumps(request.session.get("user"), indent=4),
        #},
    )

def getSettingsToken(request):
    value = authorizeToken(request)
    return JsonResponse({"token": settings.BACKEND_SETTINGS})