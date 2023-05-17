"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling test calls and getting a csrf cookie
"""

from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt, csrf_protect, requires_csrf_token, ensure_csrf_cookie

# this makes it possible to assume for a function, that certain requests are passed through
from django.views.decorators.http import require_http_methods

###################################################
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

###################################################
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

###################################################
from channels.generic.websocket import AsyncWebsocketConsumer
class testWebSocket(AsyncWebsocketConsumer):
    ##########################
    async def connect(self):
        await self.accept()
    ##########################
    async def disconnect(self, code):
        pass
    ##########################
    async def receive(self, text_data=None, bytes_data=None):
        print(text_data)
        await self.send(text_data="PONG")

################################################### 
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from backend_django.services import postgres
def testCallToWebsocket(request):
    if "user" in request.session:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(postgres.ProfileManagement.getUserKeyWOSC(session=request.session), {
    "type": "sendMessage",
    "text": "Hello there!",
})

        return HttpResponse("Success", status=200)
    return HttpResponse("Not Logged In", status=401)