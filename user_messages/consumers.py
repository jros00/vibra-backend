from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
from user_messages.models import MessageGroup, Message
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class MessageGroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug(f'Connecting WebSocket for user: {self.scope["user"].id if not self.scope["user"].is_anonymous else "Anonymous"}')
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            logger.debug('Anonymous user attempted to connect, closing WebSocket')
            await self.close(code=4001)  # Unauthorized user
        else:
            self.group_id = str(self.scope['url_route']['kwargs']['group_id'])  # Ensure group_id is a string
            logger.debug(f'Adding user {self.user.id} to group: {self.group_id}')

            try:
                self.message_group = await sync_to_async(MessageGroup.objects.get)(id=self.group_id, members=self.user)
                await self.channel_layer.group_add(
                    self.group_id,
                    self.channel_name
                )
                await self.accept()
            except MessageGroup.DoesNotExist:
                logger.error(f'No message group found for user {self.user.id} and group {self.group_id}')
                await self.close(code=4002)

    async def disconnect(self, close_code):
        logger.debug(f'Removing user {self.user.id} from group: {self.group_id}')
        await self.channel_layer.group_discard(
            self.group_id,
            self.channel_name
        )

    async def receive(self, text_data):
        logger.debug(f'Received message on WebSocket from user {self.user.id}')
        try:
            message_data = json.loads(text_data)  # Attempt to parse the incoming JSON
            logger.debug(f"Parsed message data: {message_data}")  # Print the received data for inspection
            if 'message' not in message_data:
                logger.error(f"Message field missing in received data: {message_data}")
                return
            message = message_data['message']
        except json.JSONDecodeError:
            logger.error(f'Malformed message received from user {self.user.id}: {text_data}')  # Print raw message data
            return
        except KeyError as e:
            logger.error(f'KeyError - Missing field in message: {e}, Data: {text_data}')  # Log missing fields
            return
        except Exception as e:
            logger.error(f"Unexpected error when receiving message: {e}")  # Catch any other error
            return

        logger.debug(f"Message: {message} for group: {self.group_id} from user {self.user.id}")
        
        # Save message to DB asynchronously
        await sync_to_async(Message.objects.create)(
            sender=self.user,
            recipient=self.message_group,
            content=message
        )

        # Broadcast message to group
        await self.channel_layer.group_send(
            self.group_id,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username
            }
        )

    async def chat_message(self, event):
        logger.debug(f'chat_message event received for group {self.group_id} with message: {event}')
        try:
            message = event['message']
            sender = message['sender']
        except KeyError as e:
            logger.error(f'KeyError in chat_message: {e}, Event: {event}')  # Catch missing fields in event
            return

        # Mark unread messages as read asynchronously
        await sync_to_async(self.mark_messages_as_read)(sender)

        await self.send(text_data=json.dumps({
            'message': message
        }))

    def mark_messages_as_read(self, sender):
        unread_messages = Message.objects.filter(
            recipient=self.message_group,
            is_read=False,
            sender__username=sender
        )
        unread_messages.update(is_read=True)
