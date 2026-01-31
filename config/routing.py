from django.urls import path

from apps.chat.consumers import EchoConsumer
from apps.chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns

websocket_urlpatterns = [
    path("ws/echo/", EchoConsumer.as_asgi()),
    *chat_websocket_urlpatterns,
]
