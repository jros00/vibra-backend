from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger(__name__)

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug(f'Connecting WebSocket for user: {self.scope["user"].id if not self.scope["user"].is_anonymous else "Anonymous"}')
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            logger.debug('Anonymous user attempted to connect, closing WebSocket')
            await self.close(code=4001)  # Unauthorized user
        else:
            self.group_name = f"user_{self.user.id}"
            logger.debug(f'Adding user {self.user.id} to group: {self.group_name}')
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        logger.debug(f'Removing user {self.user.id} from group: {self.group_name}')
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        logger.debug(f'Received message on WebSocket from user {self.user.id}')
        try:
            message_data = json.loads(text_data)
        except json.JSONDecodeError:
            logger.error(f'Malformed message received from user {self.user.id}')
            return
        
        message = message_data['message']
        recipient_id = message_data['recipient_id']
        logger.debug(f"Message: {message} for recipient: {recipient_id} from user {self.user.id}")
        
        # Broadcast message to the recipient's group
        await self.channel_layer.group_send(
            f"user_{recipient_id}",
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username  # Add sender information
            }
        )

    async def chat_message(self, event):
        # Event received from group_send
        logger.debug(f'chat_message event called for user {self.user.id}')
        message = event['message']
        sender = event['sender']

        # Send the message back to the client WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
