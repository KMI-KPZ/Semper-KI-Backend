"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Handlers for managing the services
"""
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse

from ..serviceManager import serviceManager

###################################################
@require_http_methods(["GET"])
def getServices(request):
    """
    Return the offered services

    :param request: The request object
    :type request: Dict
    :return: The Services as dictionary with string and integer coding
    :rtype: JSONResponse
    
    """

    return JsonResponse(serviceManager.getAllServices())