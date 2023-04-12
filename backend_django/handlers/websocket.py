"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Websocket for various stuff
"""

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer

###################################################
class GeneralWebSocket(AsyncWebsocketConsumer):
    ##########################
    async def connect(self):
        await self.accept()

    ##########################
    async def disconnect(self, code):
        raise StopConsumer("Connection closed")
    
    ##########################
    async def receive(self, text_data=None, bytes_data=None):
        #if (text_data == )
        await self.send(text_data="PONG")