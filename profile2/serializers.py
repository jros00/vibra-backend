from rest_framework import serializers
from .models import Profile
from action.models import UserPreference
from core.serializers import TrackSerializer


'''
Make sure you get the liked track from userpreference. 
Send the request in the same format as in for_you/recommend for it to be possible for frontend 
to reuse existing code and not create everything from scratch.
'''
class ProfileSerializer(serializers.Serializer):

    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    liked_tracks = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'last_name', 'profile_picture', 'biography', 'followers', 'following', 'liked_tracks']
    
    def get_followers(self, obj):
        return obj.followers_count()
    
    def get_following(self, obj):
        return obj.following_count()
    
    def get_liked_tracks(self, data):
        user = data.get('username')
        user_preferences = UserPreference.objects.filter(user=user, preference='like').order_by('-timestamp')
        liked_tracks = [pref.track for pref in user_preferences]
        serializer = TrackSerializer(liked_tracks, many=True)
        return serializer.data
        
        
        
    