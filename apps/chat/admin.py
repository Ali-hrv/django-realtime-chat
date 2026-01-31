from django.contrib import admin

from apps.chat.models import Message, Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "sender", "content", "created_at")
    list_filter = ("sender", "created_at")
    search_fields = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
