from django.contrib import admin
from .models import *

class DeviceAdmin(admin.ModelAdmin):
    # List view configuration
    list_display = ('name', 'mac_address', 'ip_address', 'registered_at')
    search_fields = ('name', 'mac_address')
    list_filter = ('registered_at',)

admin.site.register(Device, DeviceAdmin)


class IntruderLogAdmin(admin.ModelAdmin):
    # List view configuration
    list_display = ('mac_address', 'ip_address', 'detected_at')
    search_fields = ('mac_address', 'ip_address')
    list_filter = ('detected_at',)

admin.site.register(IntruderLog, IntruderLogAdmin)