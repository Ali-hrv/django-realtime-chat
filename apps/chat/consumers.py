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
