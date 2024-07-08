"""
Part of Semper-KI software

Akshay NS 2024

Contains: Views for payments
"""
from django.http import JsonResponse
from .paypal_utils import create_paypal_order, capture_paypal_order

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

###################################################################

#########################################################################
# create_order
#########################################################################
#TODO Add serializer for create_order
#########################################################################
# Handler
@extend_schema(
    summary='Create an order',
    description='Create an order',
    tags=['payments'],
    request=None,
    responses={
        200: None,
        500: ExceptionSerializer
    }
)
def create_order(request):
    amount = request.GET.get('amount', '10.00')  # Default amount
    currency = request.GET.get('currency', 'USD')  # Default currency
    order = create_paypal_order(amount, currency)
    return JsonResponse(order)

#################################################################
def capture_order(request, order_id):
    capture = capture_paypal_order(order_id)
    return JsonResponse(capture)
