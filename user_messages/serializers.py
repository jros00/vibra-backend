from rest_framework import serializers
from .models import Message, MessageGroup
from django.contrib.auth.models import User
from core.serializers import TrackSerializer
from profile2.models import Profile


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    recipient = serializers.StringRelatedField()
    track = TrackSerializer(read_only=True, allow_null=True)  

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'timestamp', 'track']
    
    def get_sender(self, instance):
        request = self.context.get('request')
        user = instance.sender
        profile_picture_url = Profile.objects.get(user=user).profile_picture.url
        absolute_url = request.build_absolute_uri(profile_picture_url) if request else profile_picture_url
        return {
            'username': user.username,
            'profile_picture': absolute_url
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = self.get_sender(instance)
        return data
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class MessageGroupSerializer(serializers.ModelSerializer):
    creator = UserSerializer()  # Separate creator field
    participants = serializers.SerializerMethodField()  # Combined creator + members
    latest_message = serializers.SerializerMethodField() 
    created = serializers.DateTimeField(source='timestamp')
    
    class Meta:
        model = MessageGroup
        fields = ['id', 'group_name', 'creator', 'participants', 'created', 'latest_message']  # Include creator and participants

    def get_participants(self, obj):
        # Serialize the creator and members
        participants = UserSerializer(obj.members.all(), many=True).data
        return participants
    
    def get_latest_message(self, obj):
        # Fetch the latest message for the group
        latest_message = Message.objects.filter(recipient=obj).order_by('-timestamp').first()
        
        # If there is a message, serialize it. Otherwise, return None.
        if latest_message:
            return MessageSerializer(latest_message).data
        return None