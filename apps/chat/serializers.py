from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.chat.models import Message, Room

User = get_user_model()


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "name", "created_at")


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "room", "sender", "content", "created_at")
        read_only_fields = ("id", "sender", "created_at")


class AddRoomMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value: int):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found!")
        return value
