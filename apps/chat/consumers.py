import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer


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
        message = payload.get("message", "")

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "room_id": self.room_id,
                "message": message,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
