"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Views for some backend websites
"""
import threading

from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from logging import getLogger

logger = getLogger("django")


#######################################################
def landingPage(request):
    """
    Landing page for the backend

    :param request: GET request
    :type request: HTTP GET
    :return: Rendered page
    :rtype: None

    """
    return render(
        request,
        "landingPage.html"  # ,
        # context={
        #    "session": request.session.get("user"),
        # "pretty": json.dumps(request.session.get("user"), indent=4),
        # },
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
        "benchy.html"  # ,
        # context={
        #    "session": request.session.get("user"),
        # "pretty": json.dumps(request.session.get("user"), indent=4),
        # },
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
    # response = HttpResponse()
    # construct the file's path
    # url=os.path.join(settings.BASE_DIR,'doc','build','html','index.html')
    # response['Content-Type']=""
    # response['X-Accel-Redirect'] = url
    # return response
    pathOfHtml = request.path.replace('public/doc/', '').replace('index.html', '')
    logger.info(pathOfHtml)
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
        "sparql.html"  # ,
        # context={
        #    "session": request.session.get("user"),
        # "pretty": json.dumps(request.session.get("user"), indent=4),
        # },
    )


def get_settings_token(request):
    return JsonResponse({"token": settings.BACKEND_SETTINGS})


def send_contact_form(request):
    from backend_django.services.mailer import KissMailer
    import logging
    import json
    # log whole post request
    logger = logging.getLogger('django')
    logger.info(f'recieved contact form input: "{str(request.body)}')
    print("sending email")
    data = json.loads(request.body.decode("utf-8"))
    mailer = KissMailer()
    msg = "Backendsettings: " + settings.BACKEND_SETTINGS + "\nName: " + data["name"] + "\n" + "Email: " + data[
        "email"] + "\n" + "Message: " + data["message"]
    result = mailer.sendmail(settings.EMAIL_ADDR_SUPPORT, data["subject"], msg)
    return JsonResponse({"status": "ok", "result": result})
