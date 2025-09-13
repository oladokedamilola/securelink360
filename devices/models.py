#devices/models.py
from django.db import models
from django.conf import settings


class Device(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
        db_index=True,
    )
    name = models.CharField(max_length=100, blank=True)
    mac_address = models.CharField(max_length=17, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)  # optional

    class Meta:
        indexes = [
            models.Index(fields=["mac_address"]),
            models.Index(fields=["user"]),
        ]

    def company(self):
        """Convenience: company of the owning user if assigned."""
        return self.user.company if self.user else None

    def __str__(self):
        owner = self.user.email if self.user else "Unassigned"
        return f"{self.name or self.mac_address} ({owner})"
