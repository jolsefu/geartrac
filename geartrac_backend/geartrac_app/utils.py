from .models import CustomNotification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User

def create_and_send_notification(user: User, message: str ):
    notification = CustomNotification.objects.create(
        user=user,
        message=message,
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "notification": {
                "message": notification.message,
                "timestamp": str(notification.timestamp),
                "read": notification.read
            }
        }
    )
