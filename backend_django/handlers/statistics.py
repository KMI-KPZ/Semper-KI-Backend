from django.contrib.sessions.models import Session
from django.utils import timezone
from django.http import JsonResponse

from .authentification import checkIfTokenExpired

##############################################
def getNumberOfUsers(request):
    """
    Return number of currently logged in users and 
    number of users that have an active session 

    :param request: GET request
    :type request: HTTP GET
    :return: json containing information
    :rtype: JSONResponse

    """
    activeSessions = Session.objects.filter(expire_date__gte=timezone.now())
    numOfActiveSessions = len(activeSessions)

    numOfLoggedInUsers = 0
    for session in activeSessions:
        data = session.get_decoded()
        if "user" in data:
            if checkIfTokenExpired(data["user"]):
                numOfLoggedInUsers += 1
    
    output = {"active": numOfActiveSessions, "loggedIn": numOfLoggedInUsers}
    return JsonResponse(output)
