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
def landingPage(request):
    """
    Landing page for the backend

    :param request: GET request
    :type request: HTTP GET
    :return: Rendered page
    :rtype: HTTPResponse

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
def docPage(request):
    """
    Documentation page for the backend

    :param request: GET request
    :type request: HTTP GET
    :return: Rendered page
    :rtype: HTTPResponse

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