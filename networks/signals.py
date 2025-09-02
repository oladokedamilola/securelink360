from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import UnauthorizedAttempt, NetworkMembership, JoinRequest
from devices.models import Device

def group_for_network(network_id: int) -> str:
    return f"network_{network_id}"

@receiver(post_save, sender=UnauthorizedAttempt)
def unauthorized_attempt_created(sender, instance, created, **kwargs):
    if not created:
        return
    channel_layer = get_channel_layer()
    payload = {
        "type": "intruder_detected",
        "attempt_id": instance.id,
        "network_id": instance.network_id,
        "ip_address": instance.ip_address,
        "mac_address": instance.mac_address,
        "reason": instance.reason,
        "timestamp": instance.created_at.isoformat(),
    }
    async_to_sync(channel_layer.group_send)(
        group_for_network(instance.network_id),
        {"type": "broadcast", "payload": payload}
    )

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
    # If you track online/offline in Device (e.g., instance.status), broadcast here
    if not instance.company_id:
        return
    # If device is tied to a specific network, include that. Otherwise, you can broadcast company-wide.
    # Assuming we attach a device to networks in your domain; if not, skip or compute
