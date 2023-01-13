import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse

def getFilter(request):
    
    return JsonResponse({}, status=500)