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
    last_seen = models.DateTimeField(null=True, blank=True)
    is_blocked = models.BooleanField(default=False) 
    STATUS_CHOICES = [
        ('offline', 'Offline'),
        ('online', 'Online'),
        ('pending', 'Pending Approval'), 
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')

    class Meta:
        indexes = [
            models.Index(fields=["mac_address"]),
            models.Index(fields=["user"]),
        ]

    def company(self):
        return self.user.company if self.user else None

    def __str__(self):
        owner = self.user.email if self.user else "Unassigned"
        return f"{self.name or self.mac_address} ({owner})"


class DeviceLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="logs")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)  # JSON/dict string of changes if needed

    def __str__(self):
        return f"{self.get_action_display()} - {self.device} by {self.user}"
