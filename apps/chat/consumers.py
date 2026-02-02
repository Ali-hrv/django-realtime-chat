import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from apps.chat.models import Message, Room


class EchoConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_json({"type": "connected"})

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

        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close(code=4401)
            return

        if not await self._room_exists(self.room_id):
            await self.close(code=4404)
            return

        is_member = await self._is_room_member(
            room_id=int(self.room_id), user_id=user.id
        )
        if not is_member:
            await self.close(code=4403)
            return

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.send_json(
            {"type": "system", "message": f"joined room {self.room_id}"}
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if not text_data:
            return

        payload = json.loads(text_data)
        content = (payload.get("message") or "").strip()
        if not content:
            return

        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.send_json(
                {"type": "error", "message": "authentication required"}
            )
            return

        saved = await self._save_message(
            room_id=int(self.room_id),
            user_id=user.id,
            content=content,
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "room_id": int(self.room_id),
                "message_id": saved["id"],
                "message": saved["content"],
                "sender_id": saved["sender_id"],
                "created_at": saved["created_at"],
            },
        )

        await self._notify_room_members(
            room_id=int(self.room_id),
            sender_id=user.id,
            message_id=saved["id"],
            content=saved["content"],
            created_at=saved["created_at"],
        )

    async def chat_message(self, event):
        await self.send_json(event)

    async def _notify_room_members(
        self,
        room_id: int,
        sender_id: int,
        message_id: int,
        content: str,
        created_at: str,
    ):
        member_ids = await self._get_room_member_ids(room_id)

        payload = {
            "room_id": room_id,
            "message_id": message_id,
            "sender_id": sender_id,
            "content_preview": content[:120],
            "created_at": created_at,
        }

        for uid in member_ids:
            if uid == sender_id:
                continue

            await self._create_notification(user_id=uid, payload=payload)

            await self.channel_layer.group_send(
                f"user_{uid}",
                {
                    "type": "notify",
                    "event": "chat.message",
                    "payload": payload,
                },
            )

    @database_sync_to_async
    def _room_exists(self, room_id: int) -> bool:
        return Room.objects.filter(id=room_id).exists()

    @database_sync_to_async
    def _is_room_member(self, room_id: int, user_id: int) -> bool:
        from apps.chat.models import RoomMember

        return RoomMember.objects.filter(room_id=room_id, user_id=user_id).exists()

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

    @database_sync_to_async
    def _get_room_member_ids(self, room_id: int) -> list[int]:
        from apps.chat.models import RoomMember

        return list(
            RoomMember.objects.filter(room_id=room_id).values_list("user_id", flat=True)
        )

    @database_sync_to_async
    def _create_notification(self, user_id: int, payload: dict) -> None:
        from apps.chat.models import Notification

        Notification.objects.create(
            user_id=user_id,
            event_type="chat.message",
            payload=payload,
        )


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.group_name = f"user_{user.id}"

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.send_json({"type": "system", "message": "notification connected"})

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event):
        await self.send_json(event)
