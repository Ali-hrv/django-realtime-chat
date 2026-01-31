import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from apps.chat.models import Message, Room


class EchoConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"type": "connected"}))

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data is not None:
            await self.send(text_data=text_data)
        if bytes_data is not None:
            await self.send(bytes_data=bytes_data)

    async def disconnect(self, close_code):
        return


class RoomChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"room_{self.room_id}"

        await self.accept()

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.send(
            text_data=json.dumps(
                {"type": "system", "message": f"joined room {self.room_id}"}
            )
        )

    async def disconnect(self, code):
        await self.channel_layer.group_descard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if not text_data:
            return

        payload = json.loads(text_data)
        content = (payload.get("message") or "").strip()
        if not content:
            return

        if (
            isinstance(self.scope.get("user"), AnonymousUser)
            or not self.scope["user"].is_autneticated
        ):
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "authentication required"}
                )
            )
            return

        message = await self._save_message(
            room_id=self.room_id,
            user_id=self.scope["user"].id,
            content=content,
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "room_id": self.room_id,
                "message_id": message["id"],
                "message": message["content"],
                "sender_id": message["sender_id"],
                "created_at": message["created_at"],
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def _save_message(self, room_id: int, user_id: int, content: str) -> dict:
        room = Room.objects.get(id=room_id)
        message = Message.objects.create(room=room, sender_id=user_id, content=content)
        return {
            "id": message.id,
            "content": message.content,
            "sender_id": message.sender_id,
            "created_at": message.created_at.isoformat(),
        }
