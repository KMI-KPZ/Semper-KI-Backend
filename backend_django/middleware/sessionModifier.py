"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Middleware that adds and removes non-serializable objects to the session dictionary. 
Must be included after the session middleware!
"""

from asgiref.sync import _iscoroutinefunction_or_partial
from django.utils.decorators import sync_and_async_middleware
from asgiref.sync import sync_to_async

from ..services.postgresDB import pgOrders, pgProfiles

@sync_and_async_middleware
def sessionModifierMiddleware(get_response):
    # One-time configuration and initialization goes here.
    def getSession(request):
        request.session.save()
        return request.session
    def setSession(request, session):
        request.session = session
        request.session.save()
        return None

    if _iscoroutinefunction_or_partial(get_response):

        async def sessionModifier(request):
            # What shall happen before other middleware
            session = await sync_to_async(getSession)(request)
            if "isPartOfOrganization" in session:
                if request.session["isPartOfOrganization"]:
                    session["pgProfileClass"] = pgProfiles.pgPOrganization
                    session["pgOrderClass"] = pgOrders.pgOOrganization
                else:
                    session["pgProfileClass"] = pgProfiles.pgPUser
                    session["pgOrderClass"] = pgOrders.pgOUser
            #await sync_to_async(setSession)(request, session)

            response = await get_response(request)

            if "pgProfileClass" in request.session:
                request.session.pop("pgProfileClass")
                request.session.pop("pgOrderClass")
            # What shall happen afterwards
            return response

    else:

        def sessionModifier(request):
            # What shall happen before other middleware
            if "isPartOfOrganization" in request.session:
                if request.session["isPartOfOrganization"]:
                    request.session["pgProfileClass"] = pgProfiles.pgPOrganization
                    request.session["pgOrderClass"] = pgOrders.pgOOrganization
                else:
                    request.session["pgProfileClass"] = pgProfiles.pgPUser
                    request.session["pgOrderClass"] = pgOrders.pgOUser

            response = get_response(request)
            # What shall happen afterwards
            if "pgProfileClass" in request.session:
                request.session.pop("pgProfileClass")
                request.session.pop("pgOrderClass")
            return response

    return sessionModifier