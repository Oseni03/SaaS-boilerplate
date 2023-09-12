from channels.generic.websocket import AsyncWebsocketConsumer
from django.template import Context, Template
from django.conf import settings
from django.template.loader import render_to_string
import json 

class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.group_name = "notifications"
        
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        
    async def send_notification(self, event):
        message = event["message"]

        rendered_notification = render_to_string(
            "websockets/notification.html",
            message
        )

        await self.send(
            text_data=json.dumps({
                "type": self.group_name,
                "message": rendered_notification
            })
        )