from django.shortcuts import render


#######################################################
def index(request):
    """
    Landing page for the backend

    :param request: GET request
    :type request: HTTP GET
    :return: Rendered page
    :rtype: None

    """
    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("user"),
            #"pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )