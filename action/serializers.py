from rest_framework import serializers
from action.models import UserPreference, ListeningHistory, GlobalPreference
from core.models import Track
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ObjectDoesNotExist


class GlobalPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalPreference
        fields = ['track', 'likes', 'dislikes']

    def create_or_update_preference(self, track, preference):
        # Check if GlobalPreference already exists for this track
        try:
            global_preference = GlobalPreference.objects.get(track=track)

            # Update the corresponding preference
            if preference == 'like':
                global_preference.likes += 1
            elif preference == 'dislike':
                global_preference.dislikes += 1

            global_preference.save()
            return global_preference

        except GlobalPreference.DoesNotExist:
            # If it doesn't exist, create a new GlobalPreference record
            if preference == 'like':
                likes = 1
                dislikes = 0
            else:
                likes = 0
                dislikes = 1

            global_preference = GlobalPreference.objects.create(track=track, likes=likes, dislikes=dislikes)
            return global_preference



class UserPreferenceSerializer(serializers.ModelSerializer):
    '''Handles likes and dislikes'''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    timestamp = serializers.DateTimeField(read_only=True)
    preference = serializers.CharField(write_only=True)
    track_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserPreference
        fields = ['user', 'preference', 'timestamp', 'track_id']

    def validate(self, data):
        track_id = data.get('track_id')
        # Check if the track exists
        if not Track.objects.filter(pk=track_id).exists():
            raise serializers.ValidationError("Track does not exist.")
        
        preference = data.get('preference')
        if preference not in ("like", "dislike"):
            raise serializers.ValidationError("Preference must be 'like' or 'dislike'.")
        
        return data

    def create(self, validated_data):
        user = validated_data.get('user')
        track_id = validated_data.get('track_id')
        new_preference = validated_data.pop('preference')

        # Retrieve the Track instance from the track_id
        track = Track.objects.get(pk=track_id)

        try:
            # Check if a UserPreference already exists for this user and track
            user_preference = UserPreference.objects.get(user=user, track=track)
            
            # Update the existing UserPreference
            old_preference = user_preference.preference
            user_preference.preference = new_preference
            user_preference.timestamp = timezone.now()
            user_preference.save()

            # Update GlobalPreference based on the change in preference
            global_preference = GlobalPreference.objects.get(track=track)
            if old_preference != new_preference:
                if old_preference == "like" and new_preference == "dislike":
                    global_preference.likes -= 1
                    global_preference.dislikes += 1
                elif old_preference == "dislike" and new_preference == "like":
                    global_preference.likes += 1
                    global_preference.dislikes -= 1
                global_preference.save()

        except UserPreference.DoesNotExist:
            # If no existing UserPreference, create a new one
            user_preference = UserPreference.objects.create(
                user=user,
                track=track,
                preference=new_preference,
                timestamp=timezone.now()
            )

            # Create or update GlobalPreference based on the new preference
            global_preference, created = GlobalPreference.objects.get_or_create(track=track)
            if new_preference == "like":
                global_preference.likes += 1
            elif new_preference == "dislike":
                global_preference.dislikes += 1
            global_preference.save()

        return user_preference


class ListeningHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for individual listening history records.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    start_listening_time = serializers.CharField(write_only=True)
    end_listening_time = serializers.CharField(write_only=True)
    track_id = serializers.IntegerField(write_only=True)
    
    # Listening time formatted as hour:min:sec
    formatted_listening_time = serializers.SerializerMethodField()

    class Meta:
        model = ListeningHistory
        fields = ['user', 'timestamp', 'track_id', 'listening_time', 'formatted_listening_time', 'start_listening_time', 'end_listening_time']

    def validate(self, data):
        """
        Validate start and end listening times and ensure the track exists.
        """
        start_time = data.get('start_listening_time')
        end_time = data.get('end_listening_time')

        # Parse datetime strings
        start_time = parse_datetime(start_time)
        end_time = parse_datetime(end_time)

        if not start_time or not end_time:
            raise serializers.ValidationError("Start and end listening times must be provided.")
        if start_time >= end_time:
            raise serializers.ValidationError("End listening time must be after start listening time.")

        # Validate track exists
        track_id = data.get('track_id')
        if not Track.objects.filter(pk=track_id).exists():
            raise serializers.ValidationError("Track does not exist.")

        # Calculate listening duration (timedelta)
        data['listening_time'] = end_time - start_time

        return data

    def create(self, validated_data):
        """
        Create or update a ListeningHistory instance after replacing track_id with the actual Track object.
        """
        validated_data.pop('start_listening_time', None)
        end_time = validated_data.pop('end_listening_time', None)

        # Replace track_id with the actual track object
        track_id = validated_data.pop('track_id')
        track = Track.objects.get(pk=track_id)
        validated_data['track'] = track

        user = self.context['request'].user

        # Use filter() to retrieve all entries for the same user and track
        listening_histories = ListeningHistory.objects.filter(user=user, track=track).order_by('-timestamp')

        if listening_histories.exists():
            # If records exist, update the most recent one
            listening_history = listening_histories.first()
            listening_history.listening_time += validated_data['listening_time']
            listening_history.timestamp = end_time  # Update timestamp to the current time
            listening_history.save()
        else:
            # If no record exists, create a new one
            listening_history = ListeningHistory.objects.create(**validated_data)

        return listening_history

    def get_formatted_listening_time(self, obj):
        """
        Return listening time in the format hh:mm:ss.
        """
        # Get the listening_time which is a timedelta object
        listening_time = obj.listening_time

        # Calculate hours, minutes, and seconds
        total_seconds = int(listening_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Return the formatted string
        return f"{hours:02}:{minutes:02}:{seconds:02}"


class MultipleListeningHistorySerializer(serializers.Serializer):
    """
    Serializer for bulk creation or update of multiple listening history records.
    """
    listening_histories = ListeningHistorySerializer(many=True)

    def create(self, validated_data):
        """
        Efficiently create or update multiple listening history records.
        """
        listening_histories_data = validated_data.get('listening_histories')
        created_or_updated_histories = []

        # Create or update each listening history record
        for listening_history_data in listening_histories_data:
            listening_history = ListeningHistorySerializer(data=listening_history_data, context=self.context)

            if listening_history.is_valid():
                created_or_updated_histories.append(listening_history.save())

        return created_or_updated_histories

    def to_representation(self, instance):
        """
        Custom representation to return the data for each created or updated ListeningHistory.
        """
        return [ListeningHistorySerializer(hist, context=self.context).data for hist in instance]
