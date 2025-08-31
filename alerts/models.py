from django.db import models

class IntruderLog(models.Model):
    mac_address = models.CharField(max_length=17)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Detected")  # Detected/Resolved

    def __str__(self):
        return f"{self.mac_address} - {self.status} at {self.timestamp}"