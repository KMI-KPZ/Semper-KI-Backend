"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Websocket for various stuff
"""

from django.http import HttpResponse

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async

from backend_django.services import postgres



# TODO 
# 1. Check if websocket is active or not -> Check
# 2. Link session to websocket (save if active or not) -> Check
# 3. Link User from database to session
# 4. Send message from one user to the other -> https://stackoverflow.com/questions/53461830/send-message-using-django-channels-from-outside-consumer-class

###################################################
class GeneralWebSocket(AsyncJsonWebsocketConsumer):
    ##########################
    def getSession(self):
        self.scope["session"].save()
        return self.scope["session"]  
     
    ##########################
    def setSession(self, key, value):
        self.scope["session"].save()
        self.scope["session"][key] = value
        self.scope["session"].save()

    ##########################
    async def connect(self):
        # check if person ist logged in or not. If not, refuse connection, if yes, allow it.
        session = await sync_to_async(self.getSession)()
        if "user" in session:
            # Then gather the user ID from the session user token and create room from that
            uID = await sync_to_async(postgres.ProfileManagement.getUserKeyWOSC)(session)
            # in other function send to that "group"/"channel"
            #TODO https://channels.readthedocs.io/en/stable/topics/channel_layers.html
            await self.channel_layer.group_add(uID, self.channel_name)
            await self.accept()

    ##########################
    async def disconnect(self, code):
        session = await sync_to_async(self.getSession)()
        if "user" in session:
            uID = await sync_to_async(postgres.ProfileManagement.getUserKeyWOSC)(session)
            await self.channel_layer.group_discard(uID, self.channel_name)
        raise StopConsumer("Connection closed")
    
    ##########################
    async def receive(self, text_data=None, bytes_data=None):
        
        await self.send(text_data="PONG")

    ##########################
    async def send(self, text_data=None, bytes_data=None, close=False):
        return await super().send(text_data, bytes_data, close)
    
    ##########################
    async def sendMessage(self, event):
        await self.send(text_data=event["text"])

    ##########################
    async def sendMessageJSON(self, event):
        await self.send_json(content=event["dict"])
