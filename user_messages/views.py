from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .models import MessageGroup, Message
from .serializers import MessageSerializer, MessageGroupSerializer
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



class MessagePage(APIView):
    def get(self, request, group_id, *args, **kwargs):
        # Fetch the MessageGroup, ensuring the requesting user is a member
        message_group = get_object_or_404(MessageGroup, id=group_id, members=request.user)
        
        # Fetch all messages for the group, ordered by timestamp
        messages = Message.objects.filter(recipient=message_group).order_by('timestamp')
        
        # Serialize and return the messages
        serializer = MessageSerializer(messages, many=True)
        return Response({
            'group_name': message_group.group_name, 
            'messages': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, group_id, *args, **kwargs):
        # Ensure the user is part of the MessageGroup
        message_group = get_object_or_404(MessageGroup, id=group_id, members=request.user)
        
        # Get content from the request
        content = request.data.get('text')
        
        # Ensure content is not empty
        if not content:
            return Response({"error": "Message content cannot be empty!"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the new message
        message = Message.objects.create(sender=request.user, recipient=message_group, content=content)
        
        # Broadcast the message to the WebSocket group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            str(group_id),  # Group name must match the one in MessageGroupConsumer
            {
                'type': 'chat_message',
                'message': content,
                'sender': request.user.username,
            }
        )
        
        # Serialize the newly created message
        serializer = MessageSerializer(message)
        
        # Return a success response with the serialized message
        return Response({
            "detail": "Message sent successfully!",
            "message": serializer.data
        }, status=status.HTTP_201_CREATED)

class ChatListPage(APIView):
    
    def get(self, request):
        user = request.user  # Get the logged-in user
        
        # Filter groups where the user is either the creator or a member
        chat_groups = MessageGroup.objects.filter(
            Q(creator=user) | Q(members=user)
        ).distinct().order_by('timestamp')  # Order the groups by timestamp
        
        # Use the MessageGroupSerializer to serialize the groups
        serializer = MessageGroupSerializer(chat_groups, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)