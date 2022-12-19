import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def loginUser(request):
    uri = oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callbackLogin"))
    )
    # return uri
    return HttpResponse(uri.url)

def callbackLogin(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token

    # token = json.dumps(token)
    #uri = request.build_absolute_uri(reverse("index"))
    forward_url = request.build_absolute_uri('http://localhost:3000/callback/login')
    response = HttpResponseRedirect(forward_url)
    #response["user"] = token # This doesnt work
    # response.set_cookie("authToken", value=token)
    return response
    #return redirect(forward_url, data=token)
    # return redirect(request.build_absolute_uri(reverse("index")))

def getAuthInformation(request):
    # TODO check if cookies are expired
    if "user" in request.session:
        response = JsonResponse(request.session["user"])
        return response
    else:
        return JsonResponse({}, status=401)

def logoutUser(request):
    request.session.clear()
    request.session.flush()

    # return redirect(
    #     f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
    #     + urlencode(
    #         {
    #             #"returnTo": request.build_absolute_uri(reverse("index")),
    #             "returnTo": request.build_absolute_uri('http://localhost:3000/callback/logout'),
    #             "client_id": settings.AUTH0_CLIENT_ID,
    #         },
    #         quote_via=quote_plus,
    #     ),
    # )
    response = HttpResponse(f"https://{settings.AUTH0_DOMAIN}/v2/logout?" + urlencode({"returnTo": request.build_absolute_uri('http://localhost:3000/callback/logout'),"client_id": settings.AUTH0_CLIENT_ID,},quote_via=quote_plus,))
    return response


def index(request):
    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("user"),
            #"pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )