from django.urls import path

from apps.chat.consumers import RoomChatConsumer

websocket_urlpatterns = [
    path("ws/chat/rooms/<int:room_id>", RoomChatConsumer.as_asgi()),
]
