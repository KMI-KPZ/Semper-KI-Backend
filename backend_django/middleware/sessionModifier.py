"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Middleware that adds and removes non-serializable objects to the session dictionary. 
Must be included after the session middleware!

DEPRECATED!!!!!
"""

from asgiref.sync import _iscoroutinefunction_or_partial
from django.utils.decorators import sync_and_async_middleware
from asgiref.sync import sync_to_async

from ..services.postgresDB import pgProcesses, pgProfiles

@sync_and_async_middleware
def sessionModifierMiddleware(get_response):
    # One-time configuration and initialization goes here.
    def getSession(request):
        sessionObj = request.session.load() # look at this
        return sessionObj

    if _iscoroutinefunction_or_partial(get_response):

        async def sessionModifier(request):
            # What shall happen before other middleware
            session = await sync_to_async(getSession)(request)
            if "iterationNumber" in session:
                session["iterationNumber"] += 1
            else:
                session["iterationNumber"] = 0

            if "isPartOfOrganization" in session:
                if session["isPartOfOrganization"]:
                    session["pgProfileClass"] = pgProfiles.pgPOrganization
                    session["pgOrderClass"] = pgProcesses.pgOOrganization
                else:
                    session["pgProfileClass"] = pgProfiles.pgPUser
                    session["pgOrderClass"] = pgProcesses.pgOUser
            #await sync_to_async(setSession)(request, session)
            response = await get_response(request) # do everything else
            
            # What shall happen afterwards
            session = await sync_to_async(getSession)(request)
            if "pgProfileClass" in session:
                session.pop("pgProfileClass")
                session.pop("pgOrderClass")
            session.save()
            return response

    else:

        def sessionModifier(request):
            # What shall happen before other middleware
            if "isPartOfOrganization" in request.session:
                if request.session["isPartOfOrganization"]:
                    request.session["pgProfileClass"] = pgProfiles.pgPOrganization
                    request.session["pgOrderClass"] = pgProcesses.pgOOrganization
                else:
                    request.session["pgProfileClass"] = pgProfiles.pgPUser
                    request.session["pgOrderClass"] = pgProcesses.pgOUser

            response = get_response(request)
            # What shall happen afterwards
            if "pgProfileClass" in request.session:
                request.session.pop("pgProfileClass")
                request.session.pop("pgOrderClass")
            return response

    return sessionModifier