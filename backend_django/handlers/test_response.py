"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling test calls and getting a csrf cookie
"""

from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt, csrf_protect, requires_csrf_token, ensure_csrf_cookie

# this makes it possible to assume for a function, that certain requests are passed through
from django.views.decorators.http import require_http_methods

#@require_http_methods(["GET", "POST"]) # get and post will make it this far
@csrf_exempt # ONLY FOR TESTING!!!!
def testResponse(request):
    """
    Tests whether request and response scheme works.

    :param request: any request
    :type request: HTTP 
    :return: Response with answer string and testheader
    :rtype: HTTP Response

    """
    outString = request.method
    response = HttpResponse(outString + " test")
    response["testHeader"] = "TESTHEADER"
    return response


#@csrf_protect
@ensure_csrf_cookie
def testResponseCsrf(request):
    """
    Ensures that the csrf cookie is set correctly.

    :param request: GET request
    :type request: HTTP GET
    :return: Response with cookie
    :rtype: HTTP Response

    """
    response = HttpResponse("CSRF worked for: " + request.method)
    return response