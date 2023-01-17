import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse

def getFilter(request):
    """
    Try to filter 3d-models according to json.

    :param request: Json containing filters
    :type request: HTTP POST
    :return: Models accoding to filters via JSON
    :rtype: JSON

    """
    # ID, name, file(picture)
    return JsonResponse({})