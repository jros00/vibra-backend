from rest_framework import serializers
from action.models import UserPreference, ListeningHistory, GlobalPreference
from core.models import Track
from django.utils import timezone


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

    

# class ListeningHistorySerializer(serializers.ModelSerializer):
#     '''
#     Handles listening history and time validation based on RequestLog.
#     '''
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     timestamp = serializers.HiddenField(default=timezone.now)
#     #track = TrackSerializer(read_only=True)

#     class Meta:
#         model = ListeningHistory
#         fields = ['user', 'timestamp', 'track', 'listening_time']

    # def validate(self, data):
    #     print('inside val')

    #     # Access the track from context and ensure it exists
    #     track = self.context.get('track_results')
    #     if track is None:
    #         raise serializers.ValidationError("Track does not exist.")

    #     # Extract track_id after validation
    #     track_id = track['track_id']
    #     data['track'] = track_id

    #     # Now check if past RequestLog objects exist for the user
    #     user = data.get('user')
    #     #past_request_logs = RequestLog.objects.filter(user=user)

    #     if past_request_logs.exists():
    #         # Get the most recent request log by timestamp
    #         last_request_log = past_request_logs.order_by('-timestamp').first()
    #         data['past_request_log'] = last_request_log
    #         print(last_request_log)

    #     # Create or validate the request log using the serializer, not the model directly
    #     request_log_serializer = RequestLogSerializer(data={'user': user, 'track': track_id})
        
    #     if request_log_serializer.is_valid():
    #         request_log = request_log_serializer.save()  # Save the request log
    #         print('log created!')
    #     else:
    #         raise serializers.ValidationError(request_log_serializer.errors)

    #     return data


    # def create(self, validated_data):
    #     # Get the user and track from the validated data
    #     print('inside_create')
    #     user = validated_data['user']
    #     track = validated_data['track']
    #     request_log = validated_data.pop('request_log')

        
    #     if past_request_logs.exists():
    #         # If past request logs exist, create ListeningHistory
    #         return ListeningHistory.objects.create(**validated_data)
    #     else:
    #         # If no past request logs exist, you can either:
    #         # - Return None (if you don't want to create ListeningHistory)
    #         # - Return some meaningful data or message indicating ListeningHistory wasn't created.
    #         raise serializers.ValidationError("Listening history not created. No previous request log found.")