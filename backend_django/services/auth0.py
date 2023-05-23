"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for oauth verification
"""

from authlib.integrations.django_client import OAuth
from django.conf import settings
import requests

oauth_auth0 = OAuth()

oauth_auth0.register(
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
    return oauth_auth0.auth0.authorize_access_token(request)

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

    return oauth_auth0.auth0.authorize_redirect(
        request, request.build_absolute_uri(callback)
    )

#######################################################################################
oauth_auth0_orga = OAuth()

oauth_auth0_orga.register(
    "auth0Orga",
    client_id=settings.AUTH0_ORGA_CLIENT_ID,
    client_secret=settings.AUTH0_ORGA_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

#######################################################
def authorizeTokenOrga(request):
    """
    Get information back from Auth0 and generate token.

    :param request: POST request
    :type request: HTTP POST
    :return: Token
    :rtype: Dictionary

    """
    return oauth_auth0_orga.auth0Orga.authorize_access_token(request)

#######################################################
def authorizeRedirectOrga(request, callback):
    """
    Authorize redirection for callback

    :param request: GET request
    :type request: HTTP GET
    :param callback: Function
    :type callback: Function
    :return: URI
    :rtype: HTTP URI

    """

    return oauth_auth0_orga.auth0Orga.authorize_redirect(
        request, request.build_absolute_uri(callback)
    )

def retrieveOrganisationName(org_id):
    """
    Ask Auth0 API for name of an organisation

    :param org_id: ID gained from oauth token
    :type org_id: str
    :return: Name of organisation
    :rtype: str

    """
    # Configuration Values
    audience = f'https://{settings.AUTH0_DOMAIN}/api/v2/'

    # Get an Access Token from Auth0
    base_url = f"https://{settings.AUTH0_DOMAIN}"
    payload =  { 
        'grant_type': "client_credentials",
        'client_id': settings.AUTH0_API_CLIENT_ID,
        'client_secret': settings.AUTH0_API_CLIENT_SECRET,
        'audience': audience
    }
    response = requests.post(f'{base_url}/oauth/token', data=payload)
    oauth = response.json()
    access_token = oauth.get('access_token')

    # Add the token to the Authorization header of the request
    headers = {
        'authorization': f'Bearer {access_token}',
        'content-Type': 'application/json'
    }

    # Get all Applications using the token
    try:
        res = requests.get(f'{base_url}/api/v2/organizations/{org_id}', headers=headers)
        print(res.json())
    except requests.HTTPError as e:
        print(f'HTTPError: {str(e.code)} {str(e.reason)}')
    except requests.URLRequired as e:
        print(f'URLRequired: {str(e.reason)}')
    except requests.RequestException as e:
        print(f'RequestException: {e}')
    except Exception as e:
        print(f'Generic Exception: {e}')
    return res.json()["display_name"]