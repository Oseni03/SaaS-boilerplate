import json 
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.template.loader import render_to_string
from apps.dashboard.models import Message

class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.group_name = "notifications"
        
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        
    async def send_notification(self, event):
        message = event["message"]

        await self.send(
            text_data=json.dumps({
                "type": event["type"],
                "message": message
            })
        )
