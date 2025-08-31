from django.db import models

class Device(models.Model):
    name = models.CharField(max_length=100)
    mac_address = models.CharField(max_length=17, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.mac_address})"

class IntruderLog(models.Model):
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17)
    detected_at = models.DateTimeField()

    def __str__(self):
        return f"Intruder {self.mac_address} @ {self.detected_at}"