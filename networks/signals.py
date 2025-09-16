# networks/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import  NetworkMembership, JoinRequest
from devices.models import Device

def group_for_network(network_id: int) -> str:
    return f"network_{network_id}"


@receiver(post_save, sender=JoinRequest)
def join_request_status_changed(sender, instance, created, **kwargs):
    if created:
        # new request event (optional)
        return
    if instance.status in ("approved", "denied"):
        channel_layer = get_channel_layer()
        payload = {
            "type": "join_request_updated",
            "request_id": instance.id,
            "status": instance.status,
            "network_id": instance.network_id,
            "user_id": instance.user_id,
        }
        async_to_sync(channel_layer.group_send)(
            group_for_network(instance.network_id),
            {"type": "broadcast", "payload": payload}
        )

@receiver(post_save, sender=NetworkMembership)
def membership_changed(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    payload = {
        "type": "membership_updated",
        "network_id": instance.network_id,
        "user_id": instance.user_id,
        "role": instance.role,
        "active": instance.active,
        "created": bool(created),
    }
    async_to_sync(channel_layer.group_send)(
        group_for_network(instance.network_id),
        {"type": "broadcast", "payload": payload}
    )

@receiver(post_save, sender=Device)
def device_state_changed(sender, instance, **kwargs):
    """
    Triggered whenever a Device is saved.
    Uses the user's company instead of a non-existent company field.
    """
    # Ensure device has a user and that user has a company
    if not instance.user or not hasattr(instance.user, "company") or instance.user.company is None:
        return

    company = instance.user.company

    # Broadcast or handle device state change per network or company
    # Replace this with your actual logic for notifying channels
    channel_layer = get_channel_layer()
    payload = {
        "type": "device_state_updated",
        "device_id": instance.id,
        "name": instance.name,
        "user_id": instance.user_id,
        "company_id": company.id,
        "mac_address": instance.mac_address,
        "ip_address": instance.ip_address,
    }

    # Example: send company-wide (adjust if you have networks attached)
    async_to_sync(channel_layer.group_send)(
        f"company_{company.id}",  # group name for the company
        {"type": "broadcast", "payload": payload}
    )
