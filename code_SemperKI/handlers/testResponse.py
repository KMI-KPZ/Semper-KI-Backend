"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handling test calls and getting a csrf cookie
"""
import platform, subprocess, json, requests

from django.http import HttpResponse, JsonResponse

# this makes it possible to assume for a function, that certain requests are passed through
from django.views.decorators.http import require_http_methods

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
    assert request, f"In {isMagazineUp.__name__}: request is empty" #Assertion
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


