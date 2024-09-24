from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from core.models import UserPreference, Track, ListeningHistory
from django.utils import timezone
from datetime import timedelta

class UserPreferenceSerializer(serializers.ModelSerializer):
    '''Is activated for likes and dislikes'''
    class Meta:
        model = UserPreference
        fields = ['activity_type','track_id']  # The fields you want to save

    def validate(self, data):
        activity_type = data.get('activity_type')
        
        if activity_type not in ("like", "dislike"):
            raise serializers.ValidationError("Activity not allowed.")
        
        # Extract track ID from the data
        track_id = data.get('track_id')
        
        # Check if track_id2 is a Track object and get its track_id. It ends up in a loop with the keys and extract the whole track object
        if isinstance(track_id, Track):
            track_id = track_id.track_id  # Extract the actual ID from the Track object

        if track_id is None:
            raise serializers.ValidationError("Missing track ID.")
        
        # Validate if the track exists in the database
        try:
            Track.objects.get(track_id=track_id)
        except Track.DoesNotExist:
            raise serializers.ValidationError({"track": "Track with this ID does not exist."})
        
        return data
        

    def create(self, validated_data):
        # Access the user from the context
        user = self.context['request'].user
        
        # Tags the activity with the current time
        time = timezone.now()
        
        # Create a new user activity and associate it with the current user
        user_preference = UserPreference.objects.create(
            user=user, 
            timestamp=time, 
            **validated_data  # Pass other validated data
        )
        print('hej')

        return user_preference

class ListeningHistorySerializer(serializers.ModelSerializer):
    '''Is activated once the user moves on to the next track'''
    class Meta:
        model = ListeningHistory
        fields = ['track_id']  # The fields you want to save

    def validate(self, data):
        previous_track_id = data.get('previous_track_id').track_id
        track_id = data.get('track_id').track_id  # from request data
        
        # Check if track_id2 is a Track object and get its track_id. It ends up in a loop with the keys and extract the whole track object
        if isinstance(previous_track_id, Track):
            previous_track_id = previous_track_id.track_id  # Extract the actual ID from the Track object
        if isinstance(track_id, Track):
            track_id = track_id.track_id
        if track_id is None or previous_track_id is None:
            raise serializers.ValidationError("Missing track ID.")
        
        # Validate if the track exists in the database
        try:
            Track.objects.get(track_id=previous_track_id)
            Track.objects.get(track_id=track_id)
        except Track.DoesNotExist:
            raise serializers.ValidationError({"track": "Track with this ID does not exist."})
        

        start_listening_time = self.context.get('start_listening_time')
        
        start_listening_time = parse_datetime(start_listening_time)
        
        if not start_listening_time:
            raise serializers.ValidationError("Invalid start listening time format.")
        
        current_time = timezone.now()
        if start_listening_time > current_time or start_listening_time < current_time - timedelta(minutes=10):
            raise serializers.ValidationError("Session expired")
        
        # Add start_listening_time to validated data for use in create method
        data['start_listening_time'] = start_listening_time
        return data

    def create(self, validated_data):
        # Access the user from the context
        user = self.context['request'].user
        
        # Tags the activity with the current time
        time = timezone.now()
        
        # Only calculate listening time, do not save start_listening_time
        start_listening_time = validated_data.pop('start_listening_time', None)
        if start_listening_time:
            listening_time = time - start_listening_time
        else:
            listening_time = None  # Set to None if it's not a "listen" activity

        user_activity = ListeningHistory.objects.create(
            user=user, 
            timestamp=time, 
            listening_time=listening_time,  # Save calculated listening time
            **validated_data  # Other validated data
            )

        return user_activity

