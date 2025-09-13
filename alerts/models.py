# alerts/models.py
from django.db import models
from django.conf import settings
from django.db import models
from django.conf import settings

class IntruderLog(models.Model):
    # If we can map the intruder to an existing device, keep link
    device = models.ForeignKey(
        "devices.Device", on_delete=models.SET_NULL, null=True, blank=True, related_name="intruder_logs"
    )
    # Who attempted (if known, null otherwise)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    mac_address = models.CharField(max_length=17, null=True, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Detected")  # Detected / Resolved
    note = models.TextField(blank=True)

    def __str__(self):
        device_str = self.device.mac_address if self.device else (self.mac_address or "unknown")
        return f"Intruder {device_str} @ {self.detected_at}"

