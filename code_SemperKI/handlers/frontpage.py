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


