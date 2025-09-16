# networks/admin.py
from django.contrib import admin
from .models import Network, NetworkMembership, JoinRequest


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    """Admin for Network model"""

    list_display = ("name", "company", "visibility", "created_at")
    list_filter = ("visibility", "company", "created_at")
    search_fields = ("name", "description", "company__name")
    ordering = ("-created_at",)


@admin.register(NetworkMembership)
class NetworkMembershipAdmin(admin.ModelAdmin):
    """Admin for NetworkMembership model"""

    list_display = ("user", "network", "role", "active", "joined_at")
    list_filter = ("role", "active", "joined_at", "network__company")
    search_fields = ("user__email", "network__name", "network__company__name")
    ordering = ("-joined_at",)


@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    """Admin for JoinRequest model"""

    list_display = ("user", "network", "device", "status", "created_at", "decided_at")
    list_filter = ("status", "created_at", "decided_at", "network__company")
    search_fields = ("user__email", "network__name", "device__mac_address")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


    