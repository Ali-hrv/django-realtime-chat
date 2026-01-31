from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.chat.models import Message, Room
from apps.chat.serializer import MessageSerializer, RoomSerializer


class StandardPageSize(PageNumberPagination):
    page_size = 10
    page_size_query_param = page_size
    max_page_size = 30


class RoomViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Room.objects.all().order_by("-created_at")
    serializer_class = RoomSerializer
    pagination_class = StandardPageSize


class MessageViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = StandardPageSize

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        return Message.objects.filter(room_id=room_id).order_by("-created_at")
