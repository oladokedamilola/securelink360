#networks/models.py
from django.db import models
from django.conf import settings
from companies.models import Company
import uuid

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

    network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name="join_requests")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="join_requests")
    device = models.ForeignKey("devices.Device", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("network", "user")

    def __str__(self):
        return f"JoinRequest({self.user.email} -> {self.network.name}, {self.status})"


class UnauthorizedAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    network = models.ForeignKey("Network", on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, default="Unauthorized network access attempt")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Unauthorized attempt by {self.user or 'Unknown'} on {self.network.name}"




