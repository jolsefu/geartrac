from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import CustomNotification
from .serializers import NotificationSerializer

@receiver(post_save, sender=CustomNotification)
def send_notification_update(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    group_name = f"user_{instance.recipient.id}"

    serializer = NotificationSerializer(instance)

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "notification": serializer.data,
            "created": created,
        }
    )
