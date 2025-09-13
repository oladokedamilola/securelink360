# alerts/admin.py
from django.contrib import admin
from .models import IntruderLog


@admin.register(IntruderLog)
class IntruderLogAdmin(admin.ModelAdmin):
    """Admin panel for IntruderLog model"""

    list_display = ("device_display", "user", "ip_address", "mac_address", "status", "detected_at")
    list_filter = ("status", "detected_at", "device", "user")
    search_fields = ("ip_address", "mac_address", "user__email", "device__mac_address")
    readonly_fields = ("detected_at",)

    def device_display(self, obj):
        return obj.device.mac_address if obj.device else "—"
    device_display.short_description = "Device"
