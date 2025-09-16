# alerts/models.py
from django.db import models
from django.conf import settings

class IntruderLog(models.Model):
    network = models.ForeignKey(  # ✅ NEW
        "networks.Network",
        on_delete=models.CASCADE,
        related_name="intruder_logs",
        null=True,
        blank=True,
        help_text="Network where the intruder attempt occurred",
    )
    device = models.ForeignKey(
        "devices.Device", on_delete=models.SET_NULL, null=True, blank=True, related_name="intruder_logs"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    mac_address = models.CharField(max_length=17, null=True, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Detected")  # Detected / Resolved
    note = models.TextField(blank=True)

    def __str__(self):
        identifier = (
            self.device.mac_address if self.device else self.mac_address or self.ip_address or "unknown"
        )
        return f"Intruder {identifier} on {self.network or 'No Network'} @ {self.detected_at}"
