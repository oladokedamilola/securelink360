# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserInvite


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin panel for the User model"""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "company", "role")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "company", "role"),
            },
        ),
    )

    list_display = ("email", "first_name", "last_name", "company", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "company")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    """Admin panel for UserInvite model"""

    list_display = ("email", "company", "role", "invited_by", "created_at", "accepted", "is_expired")
    list_filter = ("role", "accepted", "company", "created_at")
    search_fields = ("email", "invited_by__email", "company__name")
    readonly_fields = ("token", "created_at")

    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True  # ✅ shows as a boolean icon in admin
    is_expired.short_description = "Expired?"


# Site header – appears at the top of the admin panel
admin.site.site_header = "SecureLink Super Admin Dashboard"

# Site title – appears in the browser tab
admin.site.site_title = "SecureLink Admin"

# Index title – appears on the main admin index page
admin.site.index_title = "Welcome to SecureLink Super Admin Dashboard"
