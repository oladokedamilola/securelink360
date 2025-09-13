# devices/admin.py
from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Admin panel for Device model"""

    list_display = ("name", "mac_address", "ip_address", "user", "company_display", "registered_at", "last_seen")
    list_filter = ("registered_at", "last_seen", "user__company")
    search_fields = ("name", "mac_address", "ip_address", "user__email", "user__company__name")
    ordering = ("-registered_at",)
    readonly_fields = ("registered_at",)

    def company_display(self, obj):
        return obj.company()
    company_display.short_description = "Company"
