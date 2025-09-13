# companies/admin.py
from django.contrib import admin
from .models import Company, License, Announcement, Task


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin for Company model"""

    list_display = ("name", "domain", "created_at")
    search_fields = ("name", "domain")
    ordering = ("name",)
    list_filter = ("created_at",)


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    """Admin for License model"""

    list_display = ("company", "plan", "seats", "expiry_date", "is_active_display")
    list_filter = ("plan", "expiry_date")
    search_fields = ("company__name", "company__domain")
    readonly_fields = ("created_at", "key_encrypted")

    def is_active_display(self, obj):
        return obj.is_active()
    is_active_display.boolean = True
    is_active_display.short_description = "Active?"


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """Admin for Announcement model"""

    list_display = ("short_message", "scope", "company", "manager", "created_at")
    list_filter = ("scope", "company", "created_at")
    search_fields = ("message", "manager__email", "company__name")
    ordering = ("-created_at",)

    def short_message(self, obj):
        return obj.message[:50] + ("..." if len(obj.message) > 50 else "")
    short_message.short_description = "Message"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin for Task model"""

    list_display = (
        "description_short",
        "assigned_by",
        "assigned_to",
        "completed",
        "due_date",
        "created_at",
        "is_overdue_display",
    )
    list_filter = ("completed", "due_date", "created_at", "assigned_by", "assigned_to")
    search_fields = ("description", "assigned_by__email", "assigned_to__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def description_short(self, obj):
        return obj.description[:50] + ("..." if len(obj.description) > 50 else "")
    description_short.short_description = "Description"

    def is_overdue_display(self, obj):
        return obj.is_overdue()
    is_overdue_display.boolean = True
    is_overdue_display.short_description = "Overdue?"
