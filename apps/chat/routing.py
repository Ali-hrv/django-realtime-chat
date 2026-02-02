from django.urls import path

from apps.chat.consumers import EchoConsumer, NotificationConsumer, RoomChatConsumer

websocket_urlpatterns = [
    path("ws/echo/", EchoConsumer.as_asgi()),
    path("ws/chat/rooms/<int:room_id>/", RoomChatConsumer.as_asgi()),
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
