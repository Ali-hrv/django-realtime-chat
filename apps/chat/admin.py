from django.contrib import admin

from apps.chat.models import Message, Notification, Room, RoomMember


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


@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "user", "last_read_message_id", "joined_at")
    list_filter = ("room", "user")
    search_fields = ("room__name", "user__username")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "event_type", "payload", "is_read", "created_at")
    list_filter = ("event_type", "is_read")
    search_fields = ("user__username",)
