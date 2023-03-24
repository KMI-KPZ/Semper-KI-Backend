"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for oauth verification
"""

from authlib.integrations.django_client import OAuth
from django.conf import settings

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

#######################################################
def authorizeToken(request):
    """
    Get information back from Auth0 and generate token.

    :param request: POST request
    :type request: HTTP POST
    :return: Token
    :rtype: Dictionary

    """
    return oauth.auth0.authorize_access_token(request)

#######################################################
def authorizeRedirect(request, callback):
    """
    Authorize redirection for callback

    :param request: GET request
    :type request: HTTP GET
    :param callback: Function
    :type callback: Function
    :return: URI
    :rtype: HTTP URI

    """

    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(callback)
    )