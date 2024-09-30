from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import status
from .models import Message
from .serializers import MessageSerializer

class MessagePage(APIView):
    def get(self, request, recipient_id, *args, **kwargs):
        recipient = get_object_or_404(User, id=recipient_id)
        messages = Message.objects.filter(
            sender=request.user, recipient=recipient
        ) | Message.objects.filter(
            sender=recipient, recipient=request.user
        ).order_by('timestamp')

        serializer = MessageSerializer(messages, many=True)
        return Response({'recipient': recipient.username, 'messages': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, recipient_id, *args, **kwargs):
        recipient = get_object_or_404(User, id=recipient_id)
        content = request.data.get('content')
        if content:
            Message.objects.create(sender=request.user, recipient=recipient, content=content)
            return Response({"detail": "Message sent successfully!"}, status=status.HTTP_201_CREATED)
        return Response({"error": "Message content cannot be empty!"}, status=status.HTTP_400_BAD_REQUEST)
