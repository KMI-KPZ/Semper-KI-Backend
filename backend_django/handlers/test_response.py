from django.shortcuts import render

from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt, csrf_protect

# this makes it possible to assume for a function, that certain requests are passed through
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"]) # get and post will make it this far
@csrf_exempt # ONLY FOR TESTING!!!!
def test_response(request):
    if request.method == "GET":
        return HttpResponse("Hello, world. GET")
    elif request.method == "POST":
        print(request)
        print(request.body)
        return HttpResponse("Hello, world. POST")
    else:
        return HttpResponse("Hello, world. " + request.method)

@csrf_protect
def test_response_csrf(request):
    return HttpResponse("CSRF worked for: " + request.method)