"""
ASGI config for backend_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_django.settings')

# application = get_asgi_application()


import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path
from backend_django.handlers.test_response import testWebSocket

websockets = [
    path("ws/testWebsocket/", testWebSocket.as_asgi(), name="testAsync")
]

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_django.settings.base")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "https": get_asgi_application(),
        "websocket":URLRouter(websockets) #AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(websockets))),
    }
)