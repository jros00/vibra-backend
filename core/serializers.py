from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from core.models import UserPreference, Track, ListeningHistory, AudioFeature, RequestLog
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class AudioFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFeature
        fields = ['chroma_mean', 'tempo', 'mfcc_mean']


class TrackSerializer(serializers.ModelSerializer):
    '''Returns the full data of the Track, including its audio features'''
    audio_features = AudioFeatureSerializer(read_only=True)

    class Meta:
        model = Track
        fields = ['track_id', 'track_title', 'artist_name', 'audio_url', 'audio_features']
        read_only_fields = ['track_id']

    
    def to_representation(self, instance):
        '''
        Override the to_representation method to include audio features
        when returning the data.
        '''
        representation = super().to_representation(instance)

        # Correctly access the reverse relationship for audio features
        try:
            # Assuming AudioFeature has a ForeignKey or OneToOneField to Track
            audio_features = instance.audiofeature  # Access the reverse relationship
            representation['audio_features'] = AudioFeatureSerializer(audio_features).data
        except AudioFeature.DoesNotExist:
            representation['audio_features'] = None  # Handle the case when no audio features exist

        return representation



class UserPreferenceSerializer(serializers.ModelSerializer):
    '''Handles likes and dislikes'''
    track = TrackSerializer(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserPreference
        fields = ['user', 'activity_type', 'time_stamp', 'track']  # The fields you want to save

    def validate(self, data):
        # Ensure the track exists
        track = get_object_or_404(Track, track_id=data.get('track_id'))
        data['track'] = track  # Use ForeignKey relationship directly

        activity_type = data.get('activity_type')
        if activity_type not in ("like", "dislike"):
            raise serializers.ValidationError("Activity type not allowed.")

        data['time_stamp'] = timezone.now()
        return data


class RequestLogSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    timestamp = serializers.HiddenField(default=timezone.now)

    class Meta:
        model = RequestLog
        fields = ['user', 'track', 'timestamp']

    def create(self, validated_data):
        # Always create the RequestLog object
        return RequestLog.objects.create(**validated_data)


class ListeningHistorySerializer(serializers.ModelSerializer):
    '''
    Handles listening history and time validation based on RequestLog.
    '''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    timestamp = serializers.HiddenField(default=timezone.now)
    track = TrackSerializer(read_only=True)

    class Meta:
        model = ListeningHistory
        fields = ['user', 'timestamp', 'track', 'listening_time']

    def validate(self, data):
        print('inside val')
        # Ensure track exists and perform validation
        print(data)
        track = self.context.get('track_results')
        track_id = track['track_id']
        if track is None:
            raise serializers.ValidationError("Track does not exist.")
        data['track'] = track_id
        return data

    def create(self, validated_data):
        # Get the user and track from the validated data
        print('inside_create')
        user = validated_data['user']
        track = validated_data['track']

        # Create the RequestLog first (this happens always)
        request_log_data = {
            'user': user,
            'track': track,
            'timestamp': timezone.now()
        }

        request_log_serializer = RequestLogSerializer(data=request_log_data)
        if request_log_serializer.is_valid():
            request_log = request_log_serializer.save()  # Always save the request log
        else:
            raise serializers.ValidationError(request_log_serializer.errors)

        # Now check if past RequestLog objects exist for the user
        past_request_logs = RequestLog.objects.filter(user=user).exclude(id=request_log.id)

        if past_request_logs.exists():
            # If past request logs exist, create ListeningHistory
            return ListeningHistory.objects.create(**validated_data)
        else:
            # If no past request logs exist, you can either:
            # - Return None (if you don't want to create ListeningHistory)
            # - Return some meaningful data or message indicating ListeningHistory wasn't created.
            raise serializers.ValidationError("Listening history not created. No previous request log found.")