from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.chat.models import Message, Room, RoomMember
from apps.chat.serializers import (
    AddRoomMemberSerializer,
    MessageSerializer,
    RoomSerializer,
)

User = get_user_model()


class StandardPageSize(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 30


class RoomViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Room.objects.all().order_by("-created_at")
    serializer_class = RoomSerializer
    pagination_class = StandardPageSize

    @action(methods=["get", "post"], detail=True, url_path="members")
    def members(self, request, pk=None):
        room = self.get_object()

        if request.method == "GET":
            user_ids = list(
                RoomMember.objects.filter(room=room).values_list("user_id", flat=True)
            )
            return Response({"room_id": room.id, "members": user_ids})

        serializer = AddRoomMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        RoomMember.objects.get_or_create(room=room, user_id=user_id)

        return Response(
            {"status": "ok", "room_id": room.id, "added_user_id": user_id},
            status.HTTP_201_CREATED,
        )

    @action(methods=["delete"], detail=True, url_path=r"members/(?P<user_id>\d+)")
    def remove_member(self, request, pk=None, user_id=None):
        room = self.get_object()
        deleted, _ = RoomMember.objects.filter(room=room, user_id=int(user_id)).delete()

        if deleted == 0:
            return Response(
                {"detail": "Member not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"status": "ok", "room_id": room.id, "removed_user_id": int(user_id)}
        )


class MessageViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = StandardPageSize

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        return Message.objects.filter(room_id=room_id).order_by("-created_at")
