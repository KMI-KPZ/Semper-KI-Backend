"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Websocket for various stuff
"""
import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import sync_to_async

from ..connections.postgresql import pgProfiles
from ..utilities import rights

logger = logging.getLogger("django_debug")

###################################################
class GeneralWebSocket(AsyncJsonWebsocketConsumer):
    ##########################
    def getSession(self):
        return self.scope["session"].load() 
     
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
                        # in other function send to that "group"/"channel"
                        orgaIDWOSC = await sync_to_async(pgProfiles.ProfileManagementBase.getUserKeyWOSC)(uID=session["user"]["userinfo"]["org_id"])
                        await self.channel_layer.group_add(orgaIDWOSC, self.channel_name)
                        # add rights
                        for entry in rights.rightsManagement.getRightsList():
                            await self.channel_layer.group_add(orgaIDWOSC+entry, self.channel_name)

                uID = await sync_to_async(pgProfiles.ProfileManagementBase.getUserKeyWOSC)(session=session)
                await self.channel_layer.group_add(uID, self.channel_name)
                # add rights
                for entry in rights.rightsManagement.getRightsList():
                    await self.channel_layer.group_add(uID+entry, self.channel_name)
                await self.accept()
        except Exception as e:
            logger.error(f'could not connect websocket: {str(e)}')

    ##########################
    async def disconnect(self, code):
        try:
            session = await sync_to_async(self.getSession)()
            if "user" in session:
                # TODO: Signal
                # if "currentProjects" in session:
                #     await sync_to_async(saveProjectsViaWebsocket)(session)

                if "isPartOfOrganization" in session:
                    if session["isPartOfOrganization"]:
                        orgaIDWOSC = await sync_to_async(pgProfiles.ProfileManagementBase.getUserKeyWOSC)(uID=session["user"]["userinfo"]["org_id"])
                        await self.channel_layer.group_discard(orgaIDWOSC, self.channel_name)
                        for entry in rights.rightsManagement.getRightsList():
                            await self.channel_layer.group_discard(orgaIDWOSC+entry, self.channel_name)
                uID = await sync_to_async(pgProfiles.ProfileManagementBase.getUserKeyWOSC)(session=session)
                await self.channel_layer.group_discard(uID, self.channel_name)
                for entry in rights.rightsManagement.getRightsList():
                    await self.channel_layer.group_discard(uID+entry, self.channel_name)
                raise StopConsumer("Connection closed")
        except Exception as e:
            logger.error(f'could not disconnect websocket: {str(e)}')

    
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
