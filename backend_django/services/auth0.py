"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for oauth verification
"""

from authlib.integrations.django_client import OAuth
import datetime
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

#######################################################
class ManageAPIToken:
    """
    Manage oauth token class.
    """
    savedToken = {}
    accessToken = ""

    #######################################################
    def __init__(self):
        self.getAccessToken()

    #######################################################
    def getAccessToken(self):
        """
        Get initial token. Made as a function to be callable from outside. 
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
        self.accessToken = oauth.get('access_token')
        self.savedToken = oauth
        now = datetime.datetime.now()
        self.savedToken["expires_at"] = now + datetime.timedelta(seconds=oauth["expires_in"])
    
    #######################################################
    def checkIfExpired(self):
        """
        Check if token has expired and if so, request a new one. 
        """
        # check if token has expired
        if datetime.datetime.now() > self.savedToken["expires_at"]:
            # it has, request new token
            self.getAccessToken()

#######################################################
apiToken = ManageAPIToken()

#######################################################
def retrieveOrganisationName(org_id):
    """
    Ask Auth0 API for name of an organisation

    :param org_id: ID gained from oauth token
    :type org_id: str
    :return: Name of organisation
    :rtype: str

    """
    apiToken.checkIfExpired()

    # Add the token to the Authorization header of the request
    headers = {
        'authorization': f'Bearer {apiToken.accessToken}',
        'content-Type': 'application/json'
    }

    # Get all Applications using the token
    base_url = f"https://{settings.AUTH0_DOMAIN}"
    try:
        res = requests.get(f'{base_url}/api/v2/organizations/{org_id}', headers=headers)
    except requests.HTTPError as e:
        print(f'HTTPError: {str(e.code)} {str(e.reason)}')
    except requests.URLRequired as e:
        print(f'URLRequired: {str(e.reason)}')
    except requests.RequestException as e:
        print(f'RequestException: {e}')
    except Exception as e:
        print(f'Generic Exception: {e}')
    return res.json()["display_name"]