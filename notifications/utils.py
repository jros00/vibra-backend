from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def create_notification(user, message):
    Notification.objects.create(user=user, message=message)
    group_name = f"user_{user.id}"
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'message': message
        }
    )
