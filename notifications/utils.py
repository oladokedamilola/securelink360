from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

def create_notification(user, message, link=None):
    notification = Notification.objects.create(user=user, message=message, link=link)

    # Push real-time
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "notify",
                "message": message,
                "link": link,
                "timestamp": str(notification.created_at),
            }
        )
    return notification
