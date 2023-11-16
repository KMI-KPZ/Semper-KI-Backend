"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Views for some backend websites
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from logging import getLogger

logger = getLogger("django")


#######################################################
def benchyPage(request):
    """
    Landing page for the benchmark tool

    :param request: GET request
    :type request: HTTP GET
    :return: Rendered page
    :rtype: HTTPResponse

    """
    return render(
        request,
        "benchy.html"  # ,
        # context={
        #    "session": request.session.get("user"),
        # "pretty": json.dumps(request.session.get("user"), indent=4),
        # },
    )



#######################################################
def sparqlPage(request):
    """
    Landing page for a sparql test query

    :param request: GET request
    :type request: HTTP GET
    :return: Rendered page
    :rtype: HTTPResponse

    """
    return render(
        request,
        "sparql.html"  # ,
        # context={
        #    "session": request.session.get("user"),
        # "pretty": json.dumps(request.session.get("user"), indent=4),
        # },
    )


#######################################################
def getSettingsToken(request):
    """
    Return Settings of django

    :param request: GET request
    :type request: HTTP GET
    :return: JSON with Settings
    :rtype: JSONResponse
    """
    return JsonResponse({"token": settings.BACKEND_SETTINGS})

