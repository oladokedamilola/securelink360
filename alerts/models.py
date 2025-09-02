# alerts/models.py
from django.db import models
from django.conf import settings
from networks.models import UnauthorizedAttempt
import uuid
# alerts/models.py
class IntruderLog(models.Model):
    unauthorized_attempt = models.ForeignKey(UnauthorizedAttempt, on_delete=models.CASCADE)
    mac_address = models.CharField(max_length=64, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    status = models.CharField(max_length=32, default="blocked")  # blocked, flagged, etc.
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Intruder {self.mac_address or 'unknown'} at {self.timestamp}"

