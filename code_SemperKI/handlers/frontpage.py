"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Views for some backend websites
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from logging import getLogger

from ..definitions import SEMPER_KI_VERSION

logger = getLogger("django")


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
@require_http_methods(["POST"])
def checkVersionOfFrontend(request):
    """
    Check if the version of the frontend is correct. If not, log a warning.

    :param request: Information from frontend
    :type request: POST request
    :return: Version of the backend
    :rtype: JSONResponse
    
    """
    info = json.loads(request.body.decode("utf-8"))
    version = info["version"]
    if version != SEMPER_KI_VERSION:
        logger.warning(f"Backend and Frontend do not have the same version!")


    return JsonResponse({"version": SEMPER_KI_VERSION})