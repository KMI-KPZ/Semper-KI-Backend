"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Views for some backend websites
"""
from django.shortcuts import render
from django.conf import settings

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
        "landingPage.html"#,
        #context={
        #    "session": request.session.get("user"),
            #"pretty": json.dumps(request.session.get("user"), indent=4),
        #},
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
        "benchy.html"#,
        #context={
        #    "session": request.session.get("user"),
            #"pretty": json.dumps(request.session.get("user"), indent=4),
        #},
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
    #response = HttpResponse()
    # construct the file's path
    #url=os.path.join(settings.BASE_DIR,'doc','build','html','index.html')
    #response['Content-Type']=""
    #response['X-Accel-Redirect'] = url
    #return response
    pathOfHtml = request.path.replace('public/doc/', '').replace('index.html', '')
    print(pathOfHtml)
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
        "sparql.html"#,
        #context={
        #    "session": request.session.get("user"),
            #"pretty": json.dumps(request.session.get("user"), indent=4),
        #},
    )

def getSettingsToken(request):
    from django.conf import settings
    from django.http.response import JsonResponse
    return JsonResponse({"token": settings.BACKEND_SETTINGS})