from django.contrib import admin
from .models import IntruderLog

@admin.register(IntruderLog)
class IntruderLogAdmin(admin.ModelAdmin):
    list_display = ('mac_address', 'ip_address', 'timestamp', 'status')
    list_filter = ('status',)