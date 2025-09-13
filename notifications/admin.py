# notifications/admin.py
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification model"""

    list_display = ("short_message", "user", "read", "created_at", "link")
    list_filter = ("read", "created_at")
    search_fields = ("message", "user__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def short_message(self, obj):
        return obj.message[:50] + ("..." if len(obj.message) > 50 else "")
    short_message.short_description = "Message"
