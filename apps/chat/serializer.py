from rest_framework import serializers

from apps.chat.models import Message, Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "name", "created_at")


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "room", "sender", "content", "created_at")
        read_only_fields = ("id", "sender", "created_at")
