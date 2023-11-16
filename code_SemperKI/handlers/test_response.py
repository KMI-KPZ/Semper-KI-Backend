"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling test calls and getting a csrf cookie
"""
import platform, subprocess, json, requests

from django.http import HttpResponse, JsonResponse

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
@require_http_methods(["POST", "GET"])
def isMagazineUp(request):
    """
    Pings the magazine website and check if that works or not

    :param request: GET/POST request
    :type request: HTTP GET/POST
    :return: Response with True or False 
    :rtype: JSON Response

    """
    if request.method == "POST":
        try:
            content = json.loads(request.body.decode("utf-8"))
            response = {"up": True}
            for entry in content["urls"]:
                resp = requests.get(entry)
                if resp.status_code != 200:
                    response["up"] = False
                
            return JsonResponse(response)
        except Exception as e:
            return HttpResponse(e, status=500)
    elif request.method == "GET":
        param = '-n' if platform.system().lower()=='windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '2', 'magazin.semper-ki.org', '-4']

        response = {"up": True}
        pRet = subprocess.run(command)
        if pRet.returncode != 0:
            response["up"] = False
        return JsonResponse(response)


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
from backend_django.services.postgresDB import pgProfiles
def testCallToWebsocket(request):
    if "user" in request.session:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(pgProfiles.ProfileManagementBase.getUserKeyWOSC(session=request.session), {
    "type": "sendMessage",
    "text": "Hello there!",
})

        return HttpResponse("Success", status=200)
    return HttpResponse("Not Logged In", status=401)