#networks/models.py
from django.db import models
from django.conf import settings
from companies.models import Company
import uuid
from django.utils import timezone

class Network(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="networks")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=20,
        choices=[("company", "Company Only"), ("invite", "Invite Only"), ("public", "Public Discoverable")],
        default="company",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company.name})"

class NetworkSession(models.Model):
    """Tracks an active live visualization session for a network."""
    network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name="sessions")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions_created")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session for {self.network.name} by {self.created_by.email}"

    def end_session(self):
        """Method to properly end a session."""
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()

class NetworkMembership(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("employee", "Employee"),
    ]

    network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="network_memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")
    joined_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("network", "user")

    def __str__(self):
        return f"{self.user.email} in {self.network.name}"


class JoinRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("denied", "Denied"),
    ]

    ip_address = models.GenericIPAddressField(null=True, blank=True) # Track where the request came from
    network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name="join_requests")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="join_requests")
    device = models.ForeignKey("devices.Device", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decided_join_requests"
    )

    class Meta:
        unique_together = ("network", "user")

    def __str__(self):
        return f"JoinRequest({self.user.email} -> {self.network.name}, {self.status})"




