# alerts/utils.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcast_intruder_attempt(log, network_id):
    channel_layer = get_channel_layer()
    payload = {
        "type": "intruder.attempt",
        "network_id": network_id,
        "intruder": {
            "id": f"intruder_{log.id}",
            "status": "intruder",
            "ip_address": log.ip_address,
            "detected_at": log.detected_at.isoformat(),
        },
    }
    async_to_sync(channel_layer.group_send)(
        f"network_{network_id}",  # matches group used in live view
        {"type": "broadcast.message", "payload": payload},
    )
