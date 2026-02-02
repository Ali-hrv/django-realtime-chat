from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.chat.views import MessageViewSet, RoomViewSet
from apps.chat.views_ws_test import ws_test

router = DefaultRouter()
router.register(r"rooms", RoomViewSet, basename="rooms")

urlpatterns = [
    path("", include(router.urls)),
    path("rooms/<int:room_id>/messages/", MessageViewSet.as_view({"get": "list"})),
    path("ws-test/", ws_test),
]
