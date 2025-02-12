"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Basic implementations regarding the AS service
"""

from functools import wraps

from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from Generic_Backend.code_General.connections.postgresql.pgProfiles import ProfileManagementOrganization
from code_SemperKI.utilities.serializer import ExceptionSerializer

from ..service import SERVICE_NUMBER

#################### DECORATOR ###################################
def checkIfOrgaHasASAsService():
    """
    Check whether an orga can change their resources

    :return: Response whether the orga can change their resources or not. If so, call the function.
    :rtype: Response, Func
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            #Check that this orga provides AS as service
            orgaID = ProfileManagementOrganization.getOrganizationHashID(request.session)
            functionName = func.cls.__name__ if func.__name__ == "view" else func.__name__
            if SERVICE_NUMBER not in ProfileManagementOrganization.getSupportedServices(orgaID):
                message = f"Orga does not offer service in {functionName}"
                exception = "Not found"
                exceptionSerializer = ExceptionSerializer(data={"message": message, "exception": exception})
                if exceptionSerializer.is_valid():
                    return JsonResponse(exceptionSerializer.data, status=status.HTTP_404_NOT_FOUND)
                else:
                    return JsonResponse(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return func(request, *args, **kwargs)
            
        return inner

    return decorator
