from rest_framework import serializers
from .models import Profile
from action.models import UserPreference
from core.serializers import TrackSerializer


class ProfileSerializer(serializers.Serializer):
    profile_picture = serializers.ImageField()
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    biography = serializers.CharField(required=False, allow_blank=True)
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    liked_tracks = serializers.SerializerMethodField()
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    taste_profile_color = serializers.CharField(read_only=True)
    taste_profile_title = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'first_name', 'last_name', 'profile_picture', 'biography',
            'followers', 'following', 'liked_tracks', 'taste_profile_color', 'taste_profile_title'
        ]

    def get_followers(self, obj):
        return obj.followers_count()

    def get_following(self, obj):
        return obj.following_count()

    def get_liked_tracks(self, obj):
        user = obj.user
        user_preferences = UserPreference.objects.filter(user=user, preference='like').order_by('-timestamp')
        liked_tracks = [pref.track for pref in user_preferences]
        serializer = TrackSerializer(liked_tracks, many=True)
        return serializer.data

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        profile_picture_url = obj.profile_picture.url
        absolute_url = request.build_absolute_uri(profile_picture_url) if request else profile_picture_url
        return absolute_url

    def get_taste_profile_color(self, obj):
        # Return the color directly from the profile's taste_profile_color field
        return obj.taste_profile_color

    def get_taste_profile_title(self, obj):
        # Return the title directly from the profile's taste_profile_title field
        return obj.taste_profile_title