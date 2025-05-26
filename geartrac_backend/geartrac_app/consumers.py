from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.authtoken.models import Token

from .models import CustomNotification
from .serializers import NotificationSerializer

import json


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        cookies = {}
        try:
            headers = dict(self.scope["headers"])
            cookie_header = headers.get(b"cookie", b"").decode()
            for cookie in cookie_header.split(";"):
                if "=" in cookie:
                    k, v = cookie.strip().split("=", 1)
                    cookies[k] = v
        except Exception:
            cookies = {}

        token = cookies.get("access_token")

        self.user = None
        if token:
            try:
                token_obj = await Token.objects.select_related("user").aget(key=token)
                self.user = token_obj.user
            except Token.DoesNotExist:
                pass

        if not self.user:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
        await self.send(text_data=json.dumps({"message": "You are connected"}))

        @sync_to_async
        def get_serialized_notifications(user):
            notifications = CustomNotification.objects.filter(recipient=user).order_by('-timestamp')[:20]
            serializer = NotificationSerializer(notifications, many=True)
            return serializer.data

        notifications_data = await get_serialized_notifications(self.user)

        await self.send(text_data=json.dumps({
            "type": "initial_notifications",
            "notifications": notifications_data
        }))

    async def disconnect(self, close_code):
        if self.user:
            await self.channel_layer.group_discard(f"user_{self.user.id}", self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "notification_update",
            "notification": event["notification"],
            "created": event["created"],
        }))
