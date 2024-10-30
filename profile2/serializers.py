from rest_framework import serializers
from .models import Profile
from action.models import UserPreference
from core.serializers import TrackSerializer


class ProfileSerializer(serializers.Serializer):
    profile_picture = serializers.ImageField()  # Access the profile picture from Profile model
    first_name = serializers.CharField(source='user.first_name', read_only=True)  # Access the first name from the User model
    last_name = serializers.CharField(source='user.last_name', read_only=True)  # Access the last name from the User model
    biography = serializers.CharField(required=False, allow_blank=True)
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    liked_tracks = serializers.SerializerMethodField()
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)


    class Meta:
        model = Profile
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'biography', 'followers', 'following',
                  'liked_tracks']

    def get_followers(self, obj):
        return obj.followers_count()

    def get_following(self, obj):
        return obj.following_count()

    def get_liked_tracks(self, obj):  # Corrected argument from 'data' to 'obj'
        user = obj.user  # Access the user from the Profile instance
        # Fetch UserPreferences where the user liked tracks, ordered by most recent
        user_preferences = UserPreference.objects.filter(user=user, preference='like').order_by('-timestamp')
        liked_tracks = [pref.track for pref in user_preferences]  # Extract tracks from preferences
        # Use TrackSerializer to serialize the liked tracks
        serializer = TrackSerializer(liked_tracks, many=True)
        return serializer.data  # Return serialized liked tracks
    
    def get_profile_picture(self, obj):
        request = self.context.get('request')
        profile_picture_url = Profile.objects.get(user=self.id).profile_picture.url
        absolute_url = request.build_absolute_uri(profile_picture_url) if request else profile_picture_url
        return absolute_url