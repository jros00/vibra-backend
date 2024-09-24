from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from core.models import UserPreference, Track, ListeningHistory, AudioFeature
from django.utils import timezone
from datetime import timedelta
from .models import Track
from django.contrib.auth.models import User


class AudioFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFeature
        fields = ['chroma_mean', 'tempo', 'mfcc_mean']
        
        
class TrackSerializer(serializers.ModelSerializer):
    '''Returns the full data of the Track, including its audio features'''
    audio_feature = AudioFeatureSerializer(read_only=True)
    class Meta:
        model = Track
        fields = ['track_id', 'track_title', 'audio_url', 'album_image','album_name', 'audio_feature']
    
    def validate(self, track_id):
        try:
            track_id = Track.objects.get(track_id=track_id)
            try:
                AudioFeature.get(track_id=track_id)
            except AudioFeature.DoesNotExist:
                raise serializers.ValidationError("Audio features for this track could not be found.")
        except Track.DoesNotExist:
            raise serializers.ValidationError({"track": "Track with this ID does not exist."})
        return track_id

class UserPreferenceSerializer(serializers.ModelSerializer):
    '''Is activated for likes and dislikes'''
    track = TrackSerializer(read_only=True)
    
    class Meta:
        model = UserPreference
        fields = ['user', 'activity_type', 'time_stamp', 'track_id']  # The fields you want to save

    def validate(self, data):
        # Check if track instance is found using the track serializer
        user_id = self.context['request'].user
        try: 
            User.objects.get(username=user_id)
            data['user'] = user_id
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        try: 
            data.get('track')
        except:
            raise serializers.ValidationError("No track exists with this ID.")
        
        activity_type = data.get('activity_type')
        
        if activity_type not in ("like", "dislike"):
            raise serializers.ValidationError("Activity not allowed.")
        data['activity_type'] = activity_type
        data['time_stamp'] = timezone.now()
        return data
        

    def create(self, validated_data):
        '''Create a new user activity and associate it with the current user'''
        user_preference = UserPreference.objects.create(**validated_data)
        return user_preference

class ListeningHistorySerializer(serializers.ModelSerializer):
    '''Is activated once the user moves on to the next track'''
    track = TrackSerializer(read_only=True)
    class Meta:
        model = ListeningHistory
        fields = ['track_id', 'start_listening_time']  # The fields you want to save

    def validate(self, data):
        previous_track_id = data.get('previous_track_id').track_id
        
        # Check if track_id2 is a Track object and get its track_id. It ends up in a loop with the keys and extract the whole track object
        if isinstance(previous_track_id, Track):
            previous_track_id = previous_track_id.track_id  # Extract the actual ID from the Track object
        try:
            Track.get(track_id = previous_track_id)
        except:
            raise serializers.ValidationError('Previous track does not exist.') 

        track = data.get('track')
        if track is None or previous_track_id is None:
            raise serializers.ValidationError("Missing track ID.")
        
        start_listening_time = data.pop('start_listening_time', None)
        start_listening_time = parse_datetime(start_listening_time)
        
        if not start_listening_time:
            raise serializers.ValidationError("Invalid start listening time format.")
        
        current_time = timezone.now()
        if start_listening_time > current_time or start_listening_time < current_time - timedelta(minutes=30):
            raise serializers.ValidationError("Session expired")
        
        # Add start_listening_time to validated data for use in create method
        data['start_listening_time'] = start_listening_time
        
        # Access the user from the context
        user_id = self.context['request'].user
        
        user = User.get(user = user_id)
        if user is None:
            raise serializers.ValidationError("Invalid user")
        data['user'] = user.username # Add user to the fields to be processed
        data['time_stamp'] = current_time
        
        
        if not start_listening_time:
            raise serializers.ValidationError("Listening time for track could not be processed")
        
        return data

    def create(self, validated_data):
        
        # Tags the activity with the current time
        time = validated_data.get('time_stamp')
        
        # Only calculate listening time, do not save start_listening_time
        

        user_activity = ListeningHistory.objects.create(
            user=user, 
            timestamp=time, 
            listening_time=listening_time,  # Save calculated listening time
            **validated_data  # Other validated data
            )

        return user_activity

