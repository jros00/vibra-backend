from django.shortcuts import render

# Create your views here. Define what is going to happen if someone requests something.

# Implement here the numbers of likes showing on profile

#Implement 2 diff functions: 1 retrieve (get the return) and 1 list function (return all the liked songs, and sort by most recently liked)
'''
You need to make sure that one is able to run the code by sending some requests. 
This can be done in the web browser but i recommend you to install Postman or Insomnia that is easier for 
analyzing the results that the browser. 
 
Test the output by starting the server and send GET or POST requests from the specific urls
You can see all available urls by running python manage.py show_urls
'''
from django.shortcuts import render, get_object_or_404
from .models import Profile
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from .serializers import ProfileSerializer
from rest_framework import status


class ProfileView(APIView): # Use APIview or viewsets.Viewset for better error handling
    def get(self, request: Request, pk=None): # Pass the username as a product key
        try:
            # Check if valid or return error
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response('Profile does not exist', status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(profile) # Call an external serializer to get the information to send back to the frontend 
        return Response(serializer.data, status=status.HTTP_302_FOUND)
    
# Displaying the profile page and liked tracks
# def profile_view(request, username):
#     user_profile = get_object_or_404(Profile, user__username=username)
#     liked_tracks = user_profile.user.liked_tracks.all().order_by('-liked_date')
#     return render(request, 'profile.html', {
#         'user_profile': user_profile,
#         'liked_tracks': liked_tracks,
#         'followers_count': user_profile.followers_count(),
#         'following_count': user_profile.following_count(),
#     })

# Handling the biography edit
'''
Use APIview or viewsets.Viewset for better error handling.
A specific view for the own profile needs to be implemented frontend in order for this to be valid. 
If we don't, this needs to be handled by generating biography's randomly when creating new users for demo purpose. 
This should be done in core/management/commands/load_chats.py. Or this should be done either way.
'''
def edit_biography_view(request): # This should also be updated to APIview or viewsets.Viewset if used.
    # We don't implement 'edit_profile.html' frontend. 
    if request.method == 'POST':
        bio = request.POST.get('biography')
        request.user.profile.biography = bio
        request.user.profile.save()
    return render(request, 'edit_profile.html', {'profile': request.user.profile})

