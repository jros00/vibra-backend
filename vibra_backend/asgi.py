import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibra_backend.settings')
# vibra_backend/asgi
import django
django.setup()

"""
ASGI config for vibra_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from notifications.consumers import NotificationConsumer
from user_messages.consumers import MessageGroupConsumer



application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                path('ws/notifications/', NotificationConsumer.as_asgi()),
                re_path(r'ws/chat_list/chat/(?P<group_id>\d+)/$', MessageGroupConsumer.as_asgi()),
            ]
        )
    ),
})
