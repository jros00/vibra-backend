# vibra_backend/asgi
"""
ASGI config for vibra_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from notifications.consumers import NotificationConsumer
from user_messages.consumers import MessageConsumer
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibra_backend.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                path('ws/notifications/', NotificationConsumer.as_asgi()),
                path('ws/messages/', MessageConsumer.as_asgi()),
            ]
        )
    ),
})
