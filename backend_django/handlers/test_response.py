from django.shortcuts import render

from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt, csrf_protect, requires_csrf_token, ensure_csrf_cookie

# this makes it possible to assume for a function, that certain requests are passed through
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"]) # get and post will make it this far
@csrf_exempt # ONLY FOR TESTING!!!!
def test_response(request):
    outString = request.method
    response = HttpResponse(outString)
    return response


#@csrf_protect
@ensure_csrf_cookie
def test_response_csrf(request):
    response = HttpResponse("CSRF worked for: " + request.method)
    return response