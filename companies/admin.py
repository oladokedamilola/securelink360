from django.contrib import admin
from .models import Company, License

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "created_at")


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("company", "plan", "seats", "expiry_date", "is_active")
    # readonly_fields = ("key",)

    def save_model(self, request, obj, form, change):
        if not obj.key:
            obj.key = License.generate_key()
        super().save_model(request, obj, form, change)
