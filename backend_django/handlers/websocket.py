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

from backend_django.services.postgresDB import pgProfiles
from backend_django.handlers.orderManagement import saveOrderViaWebsocket

###################################################
class GeneralWebSocket(AsyncJsonWebsocketConsumer):
    ##########################
    def getSession(self, save=True):
        if save:
            self.scope["session"].save()
        return self.scope["session"]  
     
    ##########################
    def setSession(self, key, value):
        self.scope["session"].save()
        self.scope["session"][key] = value
        self.scope["session"].save()

    ##########################
    async def connect(self):
        try:
            # check if person ist logged in or not. If not, refuse connection, if yes, allow it.
            session = await sync_to_async(self.getSession)()
            if "user" in session:
                # Then gather the user ID or organization id from the session user token and create room from that
                if "isPartOfOrganization" in session:
                    if session["isPartOfOrganization"]:
                        orgaID = await sync_to_async(pgProfiles.ProfileManagementBase.getOrganization)(session)
                        # in other function send to that "group"/"channel"
                        orgaIDWOSC = await sync_to_async(pgProfiles.ProfileManagementBase.getUserKeyWOSC)(uID=orgaID["subID"])
                        await self.channel_layer.group_add(orgaIDWOSC, self.channel_name)

                uID = await sync_to_async(pgProfiles.ProfileManagementBase.getUserKeyWOSC)(session=session)
                await self.channel_layer.group_add(uID, self.channel_name)
                await self.accept()
        except Exception as e:
            print(e)

    ##########################
    async def disconnect(self, code):
        try:
            session = await sync_to_async(self.getSession)(False)
            if "user" in session:
                if "currentOrder" in session:
                    await sync_to_async(saveOrderViaWebsocket)(session)

                if "isPartOfOrganization" in session:
                    orgaID = await sync_to_async(pgProfiles.ProfileManagementBase.getOrganization)(session)
                    orgaIDWOSC = await sync_to_async(pgProfiles.ProfileManagementBase.getUserKeyWOSC)(uID=orgaID["subID"])
                    await self.channel_layer.group_discard(orgaIDWOSC, self.channel_name)

                uID = await sync_to_async(pgProfiles.ProfileManagementBase.getUserKeyWOSC)(session=session)
                await self.channel_layer.group_discard(uID, self.channel_name)
                raise StopConsumer("Connection closed")
        except Exception as e:
            print(e)

    
    ##########################
    async def receive(self, text_data=None, bytes_data=None):
        #if text_data == "Printability":

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
