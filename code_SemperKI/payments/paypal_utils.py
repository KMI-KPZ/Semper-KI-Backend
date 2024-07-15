"""
Part of Semper-KI software

Akshay NS 2024

Contains: PayPal API Integration with OAuth Token Retrieval, Order Creation, and Order Capture.
"""
import requests
from django.conf import settings
import logging

logger = logging.getLogger("logToFile")
loggerError = logging.getLogger("errors")
#################################################################################################


PAYPAL_API_BASE_URL='https://sandbox.paypal.com'
PAYPAL_CLIENT_ID='ARwAuPfJE60jW165PCJ8PduMRtFQxlmp8duwd-Ym4PVdCvTCFgfPXFRRmK4ZzKbuAHy9lVB1M_byWfpk'
PAYPAL_CLIENT_SECRET='EGSI4zGdPKuEyIp2zUDNUjv84L-bxrF20VzWWfoQ3MO1TOLxpNXswqmMOBspIrY5V_X0YJuvZ3-5C1iE'

################################################
def get_paypal_access_token():
    url = f"{PAYPAL_API_BASE_URL}/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data, auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET))

    # Log the response for debugging
    logger.debug(f"PayPal OAuth response status: {response.status_code}")
    logger.debug(f"PayPal OAuth response data: {response.json()}")

    if response.status_code != 200:
        logger.error(f"Failed to obtain access token: {response.text}")
        raise Exception(f"Failed to obtain access token: {response.text}")

    response_data = response.json()
    if 'access_token' not in response_data:
        logger.error(f"Access token not found in response: {response_data}")
        raise KeyError("access_token")

    return response_data['access_token']

#################################################################
def create_paypal_order(amount, currency="USD"):
    access_token = get_paypal_access_token()
    url = f"{PAYPAL_API_BASE_URL}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": currency,
                "value": amount
            }
        }]
    }
    response = requests.post(url, headers=headers, json=order_data)
    return response.json()

#################################################################
def capture_paypal_order(order_id):
    access_token = get_paypal_access_token()
    url = f"{PAYPAL_API_BASE_URL}/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(url, headers=headers)
    return response.json()
